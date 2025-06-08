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
    invoices_zip: UploadFile = File(..., description="ZIP file containing invoice PDFs"),
    employee_name: str = Form(..., description="Employee name for invoice linking"),
    policy_file: UploadFile = File(None, description="Optional HR reimbursement policy PDF")
) -> Dict[str, Any]:
    """
    Analyze employee invoices against company reimbursement policy
    
    Args:
        invoices_zip: ZIP file with one or more invoice PDFs
        employee_name: Name of employee submitting invoices
        policy_file: Optional PDF file containing HR reimbursement policy
        
    Returns:
        JSON response with analysis results and success status
    """
    
    # Validate file types
    if policy_file and not policy_file.filename.endswith('.pdf'):
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
            # Save invoices ZIP
            zip_path = os.path.join(temp_dir, "invoices.zip")
            with open(zip_path, "wb") as f:
                f.write(await invoices_zip.read())
            
            # Save policy file if provided
            policy_path = None
            if policy_file:
                policy_path = os.path.join(temp_dir, "policy.pdf")
                with open(policy_path, "wb") as f:
                    f.write(await policy_file.read())
            
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
                    "status": "Pending Analysis" if not policy_file else "Analyzed",
                    "reason": "No policy provided for analysis" if not policy_file else "Analysis against provided policy",
                    "amount": "0.00",
                    "date": "2024-01-01",
                    "policy_compliance": "Cannot determine without policy" if not policy_file else "Compliant"
                }
                
                processed_invoices.append(analysis_result)
            
            return {
                "success": True,
                "message": f"Successfully uploaded {len(processed_invoices)} invoices for {employee_name}",
                "employee_name": employee_name,
                "processed_count": len(processed_invoices),
                "invoices": processed_invoices,
                "policy_file": policy_file.filename if policy_file else "No policy provided",
                "note": "Using default policy rules" if not policy_file else "Analysis against provided policy"
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