"""
Invoice Analysis Endpoint - Part 1 of the assignment
Handles PDF policy and invoice ZIP file uploads for LLM analysis
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import List, Dict, Any
import tempfile
import os
import zipfile

router = APIRouter(prefix="/api/v1", tags=["Invoice Analysis"])

@router.post("/analyze-invoices")
async def analyze_invoices(
    policy_file: UploadFile = File(..., description="HR reimbursement policy PDF"),
    invoices_zip: UploadFile = File(..., description="ZIP file containing invoice PDFs"),
    employee_name: str = Form(..., description="Employee name for invoice linking")
) -> Dict[str, Any]:
    """
    Analyze employee invoices against company reimbursement policy
    
    Args:
        policy_file: PDF file containing HR reimbursement policy
        invoices_zip: ZIP file with one or more invoice PDFs
        employee_name: Name of employee submitting invoices
        
    Returns:
        JSON response with analysis results and success status
    """
    
    # Validate file types
    if not policy_file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Policy file must be a PDF"
        )
    
    if not invoices_zip.filename.endswith('.zip'):
        raise HTTPException(
            status_code=400, 
            detail="Invoices must be submitted as ZIP file"
        )
    
    try:
        # Process files in temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            policy_path = os.path.join(temp_dir, "policy.pdf")
            zip_path = os.path.join(temp_dir, "invoices.zip")
            
            # Write policy file
            with open(policy_path, "wb") as f:
                f.write(await policy_file.read())
            
            # Write invoices ZIP
            with open(zip_path, "wb") as f:
                f.write(await invoices_zip.read())
            
            # Extract invoices
            extract_dir = os.path.join(temp_dir, "invoices")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find PDF files in extracted directory
            pdf_files = [f for f in os.listdir(extract_dir) if f.endswith('.pdf')]
            
            if not pdf_files:
                raise HTTPException(
                    status_code=400, 
                    detail="No PDF files found in ZIP archive"
                )
            
            # Process each invoice (placeholder for LLM analysis)
            processed_invoices = []
            
            for pdf_file in pdf_files:
                # TODO: Replace with actual LLM analysis
                analysis_result = {
                    "invoice_id": pdf_file.replace('.pdf', ''),
                    "employee_name": employee_name,
                    "file_name": pdf_file,
                    "status": "Pending Analysis",
                    "reason": "LLM analysis not yet implemented",
                    "amount": "0.00",
                    "date": "2024-01-01",
                    "policy_compliance": "Not analyzed"
                }
                
                processed_invoices.append(analysis_result)
            
            return {
                "success": True,
                "message": f"Successfully uploaded {len(processed_invoices)} invoices for {employee_name}",
                "employee_name": employee_name,
                "processed_count": len(processed_invoices),
                "invoices": processed_invoices,
                "policy_file": policy_file.filename
            }
            
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=400, 
            detail="Invalid ZIP file format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Processing failed: {str(e)}"
        )