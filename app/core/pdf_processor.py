"""
PDF Processing utilities for Invoice Reimbursement System
Handles extraction of text from PDF files
"""

import PyPDF2
import pdfplumber
from typing import Dict, List, Optional
import os

class PDFProcessor:
    """Handle PDF text extraction and processing"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text from PDF using PyPDF2
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"PyPDF2 extraction failed: {str(e)}")
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber (better for complex layouts)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"PDFPlumber extraction failed: {str(e)}")
    
    def extract_text(self, pdf_path: str, method: str = "pdfplumber") -> str:
        """
        Extract text from PDF using specified method
        
        Args:
            pdf_path: Path to PDF file
            method: Extraction method ("pypdf2" or "pdfplumber")
            
        Returns:
            Extracted text content
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        try:
            if method == "pypdf2":
                return self.extract_text_pypdf2(pdf_path)
            elif method == "pdfplumber":
                return self.extract_text_pdfplumber(pdf_path)
            else:
                # Try pdfplumber first, fallback to PyPDF2
                try:
                    return self.extract_text_pdfplumber(pdf_path)
                except:
                    return self.extract_text_pypdf2(pdf_path)
                    
        except Exception as e:
            raise Exception(f"PDF text extraction failed: {str(e)}")
    
    def extract_invoice_data(self, pdf_path: str) -> Dict[str, str]:
        """
        Extract structured data from invoice PDF
        
        Args:
            pdf_path: Path to invoice PDF
            
        Returns:
            Dictionary with invoice data
        """
        text = self.extract_text(pdf_path)
        
        # Basic invoice data extraction (can be enhanced with regex patterns)
        invoice_data = {
            "raw_text": text,
            "file_name": os.path.basename(pdf_path),
            "word_count": len(text.split()),
            "char_count": len(text)
        }
        
        return invoice_data
    
    def extract_policy_text(self, pdf_path: str) -> str:
        """
        Extract text from HR policy PDF
        
        Args:
            pdf_path: Path to policy PDF
            
        Returns:
            Policy text content
        """
        return self.extract_text(pdf_path)