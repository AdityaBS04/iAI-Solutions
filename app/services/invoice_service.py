"""
Invoice Analysis Service
Business logic for processing invoices and storing analysis results
"""

import os
import zipfile
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.pdf_processor import PDFProcessor
from app.core.llm_client import LLMClient
from app.core.embeddings import EmbeddingGenerator
from app.core.vector_store import VectorStoreManager
from app.models.data_models import InvoiceRecord, AnalysisResult, ReimbursementStatus
from app.utils.exceptions import ProcessingError
from config import settings

class InvoiceAnalysisService:
    """Service for handling invoice analysis workflow"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.llm_client = LLMClient()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStoreManager(persist_directory=settings.vector_db_path)
    
    async def process_invoices(self, 
                             invoices_zip_path: str, 
                             employee_name: str,
                             policy_text: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Process all invoices in ZIP file
        
        Args:
            invoices_zip_path: Path to ZIP file containing invoices
            employee_name: Name of employee submitting invoices
            policy_text: Optional company policy text
            
        Returns:
            List of processed invoice results
        """
        try:
            # Extract invoices from ZIP
            invoice_files = self._extract_invoices(invoices_zip_path)
            
            processed_invoices = []
            
            for invoice_path in invoice_files:
                try:
                    # Process single invoice
                    result = await self._process_single_invoice(
                        invoice_path, 
                        employee_name, 
                        policy_text
                    )
                    processed_invoices.append(result)
                    
                except Exception as e:
                    # Handle individual invoice processing errors
                    error_result = {
                        "invoice_id": os.path.basename(invoice_path).replace('.pdf', ''),
                        "employee_name": employee_name,
                        "file_name": os.path.basename(invoice_path),
                        "status": "Analysis Failed",
                        "reason": f"Processing error: {str(e)}",
                        "reimbursable_amount": "0.00",
                        "total_amount": "0.00",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "policy_compliance": "Error"
                    }
                    processed_invoices.append(error_result)
            
            return processed_invoices
            
        except Exception as e:
            raise ProcessingError(f"Invoice processing failed: {str(e)}")
    
    async def _process_single_invoice(self, 
                                    invoice_path: str, 
                                    employee_name: str,
                                    policy_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a single invoice file
        
        Args:
            invoice_path: Path to invoice PDF
            employee_name: Employee name
            policy_text: Optional policy text
            
        Returns:
            Processing result dictionary
        """
        # Extract text from PDF
        invoice_text = self.pdf_processor.extract_text(invoice_path)
        invoice_id = os.path.basename(invoice_path).replace('.pdf', '')
        
        # Analyze with LLM
        analysis_result = self.llm_client.analyze_invoice(
            invoice_text=invoice_text,
            employee_name=employee_name,
            policy_text=policy_text
        )
        
        # Create invoice record
        invoice_record = InvoiceRecord(
            invoice_id=invoice_id,
            employee_name=employee_name,
            file_name=os.path.basename(invoice_path),
            raw_text=invoice_text,
            analysis_result=AnalysisResult(**analysis_result)
        )
        
        # Generate embedding
        embedding = self.embedding_generator.create_invoice_embedding({
            "raw_text": invoice_text,
            "reason": analysis_result.get("reason", ""),
            "status": analysis_result.get("status", ""),
            "employee_name": employee_name
        })
        
        # Store in vector database
        doc_id = self.vector_store.add_invoice(
            invoice_data={
                "invoice_id": invoice_id,
                "employee_name": employee_name,
                "status": analysis_result.get("status", "Unknown"),
                "reason": analysis_result.get("reason", ""),
                "reimbursable_amount": str(analysis_result.get("reimbursable_amount", "0.00")),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "file_name": os.path.basename(invoice_path)
            },
            embedding=embedding
        )
        
        # Return formatted result
        return {
            "invoice_id": invoice_id,
            "employee_name": employee_name,
            "file_name": os.path.basename(invoice_path),
            "status": analysis_result.get("status", "Unknown"),
            "reason": analysis_result.get("reason", "No reason provided"),
            "reimbursable_amount": str(analysis_result.get("reimbursable_amount", "0.00")),
            "total_amount": str(analysis_result.get("total_amount", "0.00")),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "policy_compliance": "Analyzed",
            "document_id": doc_id
        }
    
    def _extract_invoices(self, zip_path: str) -> List[str]:
        """
        Extract PDF files from ZIP archive
        
        Args:
            zip_path: Path to ZIP file
            
        Returns:
            List of extracted PDF file paths
        """
        try:
            extracted_files = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find all PDF files
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            file_path = os.path.join(root, file)
                            # Copy to a permanent location for processing
                            extracted_files.append(file_path)
            
            if not extracted_files:
                raise ProcessingError("No PDF files found in ZIP archive")
            
            return extracted_files
            
        except zipfile.BadZipFile:
            raise ProcessingError("Invalid ZIP file format")
        except Exception as e:
            raise ProcessingError(f"ZIP extraction failed: {str(e)}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about processed invoices
        
        Returns:
            Processing statistics
        """
        try:
            stats = self.vector_store.get_collection_stats()
            return {
                "total_processed": stats.get("document_count", 0),
                "collection_status": stats.get("status", "unknown"),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "total_processed": 0,
                "collection_status": "error", 
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }