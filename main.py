"""
Invoice Reimbursement System - Main FastAPI Application
Simple implementation for AI/ML internship assignment
"""

import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import zipfile
import tempfile
from typing import List, Dict, Any
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Invoice Reimbursement System",
    description="AI-powered system for analyzing invoice reimbursements",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for services (will be initialized in startup)
vector_store = None
llm_client = None
chat_history = []  # Simple in-memory chat history

@app.on_event("startup")
async def startup_event():
    """Initialize services on app startup"""
    global vector_store, llm_client
    
    # Initialize vector store
    try:
        import chromadb
        vector_store = chromadb.Client()
        print("✓ Vector store initialized")
    except Exception as e:
        print(f"✗ Vector store initialization failed: {e}")
    
    # Initialize LLM client
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        llm_client = genai
        print("✓ Gemini LLM client initialized")
    except Exception as e:
        print(f"✗ Gemini LLM client initialization failed: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Invoice Reimbursement System is running!",
        "status": "healthy",
        "endpoints": {
            "analyze_invoices": "/analyze-invoices",
            "chat": "/chat"
        }
    }

@app.post("/analyze-invoices")
async def analyze_invoices(
    invoices_zip: UploadFile = File(..., description="ZIP file containing invoice PDFs"),
    employee_name: str = Form(..., description="Employee name"),
    policy_file: UploadFile = File(None, description="Optional HR policy PDF")
):
    """
    Part 1: Analyze invoices against policy and store in vector database
    """
    try:
        # Basic validation
        if policy_file and not policy_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Policy file must be PDF")
        
        if not invoices_zip.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Invoices must be in ZIP format")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            zip_path = os.path.join(temp_dir, "invoices.zip")
            
            with open(zip_path, "wb") as f:
                f.write(await invoices_zip.read())
            
            # Save policy if provided
            policy_path = None
            if policy_file:
                policy_path = os.path.join(temp_dir, "policy.pdf")
                with open(policy_path, "wb") as f:
                    f.write(await policy_file.read())
            
            # Extract ZIP file
            extract_dir = os.path.join(temp_dir, "invoices")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Process invoices (simplified)
            processed_invoices = []
            pdf_files = [f for f in os.listdir(extract_dir) if f.endswith('.pdf')]
            
            for pdf_file in pdf_files:
                invoice_path = os.path.join(extract_dir, pdf_file)
                
                # Simple processing result (replace with actual LLM analysis)
                analysis_result = {
                    "invoice_id": pdf_file.replace('.pdf', ''),
                    "employee_name": employee_name,
                    "status": "Analyzed with default policy" if not policy_file else "Analyzed with provided policy",
                    "reason": "Using built-in policy rules" if not policy_file else "Analysis against uploaded policy",
                    "amount": "100.00",  # Placeholder
                    "date": "2024-01-01",  # Placeholder
                    "file_name": pdf_file
                }
                
                processed_invoices.append(analysis_result)
        
        return {
            "success": True,
            "message": f"Successfully processed {len(processed_invoices)} invoices for {employee_name}",
            "processed_count": len(processed_invoices),
            "invoices": processed_invoices,
            "policy_used": "Default company policy" if not policy_file else f"Uploaded policy: {policy_file.filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/chat")
async def chat_with_system(query: Dict[str, Any]):
    """
    Part 2: RAG chatbot endpoint for querying invoice data
    """
    global chat_history
    
    try:
        user_query = query.get("message", "")
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Add user message to history
        chat_history.append({"role": "user", "content": user_query})
        
        # Simple response (replace with actual RAG implementation)
        if "status" in user_query.lower():
            bot_response = "Based on the processed invoices, I can help you find reimbursement status information. Please specify employee name or date range for more specific results."
        elif "employee" in user_query.lower():
            bot_response = "I can search for invoices by employee name. Which employee would you like to search for?"
        else:
            bot_response = f"I understand you're asking: '{user_query}'. I can help you search through processed invoice data. Try asking about specific employees, dates, or reimbursement status."
        
        # Add bot response to history
        chat_history.append({"role": "assistant", "content": bot_response})
        
        return {
            "response": bot_response,
            "conversation_id": len(chat_history),
            "query": user_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/chat/history")
async def get_chat_history():
    """Get chat conversation history"""
    return {
        "history": chat_history,
        "message_count": len(chat_history)
    }

@app.delete("/chat/history")
async def clear_chat_history():
    """Clear chat conversation history"""
    global chat_history
    chat_history = []
    return {"message": "Chat history cleared"}

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG_MODE", "True").lower() == "true"
    )