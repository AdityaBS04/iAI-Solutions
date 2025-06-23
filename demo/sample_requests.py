"""
Sample API requests for Invoice Reimbursement System
Demonstrates how to use the API endpoints with example data
"""

import requests
import json
import os
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

class InvoiceSystemAPI:
    """Client for testing Invoice Reimbursement System API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
    
    def health_check(self):
        """Test the health check endpoint"""
        print("🔍 Testing Health Check...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            
            print("✅ Health Check Successful!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Health Check Failed: {e}")
            return None
    
    def analyze_invoices(self, policy_file_path: str, invoices_zip_path: str, employee_name: str):
        """Test the invoice analysis endpoint"""
        print(f"📄 Testing Invoice Analysis for {employee_name}...")
        
        # Validate files exist
        if not os.path.exists(policy_file_path):
            print(f"❌ Policy file not found: {policy_file_path}")
            return None
            
        if not os.path.exists(invoices_zip_path):
            print(f"❌ Invoices ZIP not found: {invoices_zip_path}")
            return None
        
        try:
            # Prepare files for upload
            with open(policy_file_path, 'rb') as policy_file, \
                 open(invoices_zip_path, 'rb') as zip_file:
                
                files = {
                    'policy_file': ('policy.pdf', policy_file, 'application/pdf'),
                    'invoices_zip': ('invoices.zip', zip_file, 'application/zip')
                }
                
                data = {
                    'employee_name': employee_name
                }
                
                response = self.session.post(
                    f"{self.api_url}/analyze-invoices",
                    files=files,
                    data=data
                )
                
                response.raise_for_status()
                result = response.json()
                
                print("✅ Invoice Analysis Successful!")
                print(f"Processed {result.get('processed_count', 0)} invoices")
                print(f"Response: {json.dumps(result, indent=2)}")
                
                return result
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Invoice Analysis Failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Error details: {e.response.text}")
            return None
    
    def chat_query(self, message: str, session_id: str = "test_session"):
        """Test the chat endpoint"""
        print(f"💬 Testing Chat Query: '{message}'...")
        
        try:
            payload = {
                "message": message,
                "session_id": session_id
            }
            
            response = self.session.post(
                f"{self.api_url}/chat",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            
            print("✅ Chat Query Successful!")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Full result: {json.dumps(result, indent=2)}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Chat Query Failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Error details: {e.response.text}")
            return None
    
    def get_chat_history(self, session_id: str = "test_session"):
        """Get chat history for a session"""
        print(f"📜 Getting Chat History for session: {session_id}...")
        
        try:
            response = self.session.get(f"{self.api_url}/chat/history/{session_id}")
            response.raise_for_status()
            result = response.json()
            
            print("✅ Chat History Retrieved!")
            print(f"Messages: {result.get('message_count', 0)}")
            print(f"History: {json.dumps(result, indent=2)}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Get Chat History Failed: {e}")
            return None
    
    def clear_chat_history(self, session_id: str = "test_session"):
        """Clear chat history for a session"""
        print(f"🗑️ Clearing Chat History for session: {session_id}...")
        
        try:
            response = self.session.delete(f"{self.api_url}/chat/history/{session_id}")
            response.raise_for_status()
            result = response.json()
            
            print("✅ Chat History Cleared!")
            print(f"Result: {json.dumps(result, indent=2)}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Clear Chat History Failed: {e}")
            return None

def run_sample_tests():
    """Run a series of sample API tests"""
    
    print("🚀 Starting Invoice Reimbursement System API Tests\n")
    
    # Initialize API client
    api = InvoiceSystemAPI()
    
    # Test 1: Health Check
    print("=" * 50)
    health_result = api.health_check()
    if not health_result:
        print("❌ API is not responding. Make sure the server is running!")
        return
    
    print("\n" + "=" * 50)
    
    # Test 2: Invoice Analysis (you'll need to provide actual file paths)
    # Update these paths to point to your actual files
    policy_file = "./data/policies/default_policy.pdf"  # Update this path
    invoices_zip = "./data/invoices/sample_invoices.zip"  # Update this path
    employee_name = "John Smith"
    
    print(f"📁 Looking for files:")
    print(f"   Policy: {policy_file}")
    print(f"   Invoices: {invoices_zip}")
    
    if os.path.exists(policy_file) and os.path.exists(invoices_zip):
        analysis_result = api.analyze_invoices(
            policy_file_path=policy_file,
            invoices_zip_path=invoices_zip,
            employee_name=employee_name
        )
    else:
        print("⚠️ Sample files not found. Please update file paths in the script.")
        print("   Creating mock analysis result for chat testing...")
        analysis_result = {"success": True, "processed_count": 3}
    
    print("\n" + "=" * 50)
    
    # Test 3: Chat Queries
    session_id = "demo_session"
    
    # Sample chat queries
    chat_queries = [
        "Hello, can you help me with invoice information?",
        f"Show me invoices for {employee_name}",
        "What invoices were fully reimbursed?",
        "Tell me about declined invoices",
        "What's the total amount of reimbursements?"
    ]
    
    for query in chat_queries:
        api.chat_query(query, session_id)
        print()
    
    print("=" * 50)
    
    # Test 4: Get Chat History
    api.get_chat_history(session_id)
    
    print("\n" + "=" * 50)
    
    # Test 5: Clear Chat History
    api.clear_chat_history(session_id)
    
    print("\n🎉 API Testing Complete!")

def create_sample_data():
    """Create sample data files for testing (optional)"""
    
    print("📝 Creating sample data files...")
    
    # Create directories
    os.makedirs("./data/policies", exist_ok=True)
    os.makedirs("./data/invoices", exist_ok=True)
    
    # Sample policy content (you can replace with actual policy)
    sample_policy = """
    COMPANY EXPENSE REIMBURSEMENT POLICY
    
    1. MEALS & ENTERTAINMENT
       - Business meals: Maximum $50 per person per day
       - Client entertainment: Maximum $100 per event with business justification
       - Alcohol: Requires special approval
    
    2. TRANSPORTATION
       - Actual costs with receipts required
       - Public transport: Full reimbursement
       - Taxi/Uber: Reasonable amounts for business purposes
    
    3. ACCOMMODATION
       - Hotel stays: Reasonable rates with receipts
       - Maximum $200 per night in major cities
       - Personal expenses not covered
    
    4. OFFICE SUPPLIES
       - Pre-approved purchases only
       - Must be business-related
       - Receipts required for all purchases
    
    5. GENERAL RULES
       - All expenses must have valid receipts
       - Business purpose must be clearly stated
       - Personal expenses are not reimbursable
       - Submit within 30 days of expense
    """
    
    # Note: This creates a text file, not a PDF
    # For actual testing, you'll need real PDF files
    with open("./data/policies/sample_policy.txt", "w") as f:
        f.write(sample_policy)
    
    print("✅ Sample policy text created at ./data/policies/sample_policy.txt")
    print("⚠️ Note: For actual testing, you need PDF files as specified in the assignment.")

if __name__ == "__main__":
    print("Invoice Reimbursement System - Sample API Requests")
    print("=" * 60)
    
    choice = input("Choose an option:\n1. Run API tests\n2. Create sample data\n3. Both\nEnter choice (1-3): ")
    
    if choice in ["2", "3"]:
        create_sample_data()
        print()
    
    if choice in ["1", "3"]:
        run_sample_tests()
    
    print("\n📚 Usage Notes:")
    print("1. Make sure your FastAPI server is running on http://localhost:8000")
    print("2. Update file paths in this script to point to your actual PDF files")
    print("3. Ensure you have valid policy PDF and invoices ZIP files")
    print("4. Check the API documentation at http://localhost:8000/docs")