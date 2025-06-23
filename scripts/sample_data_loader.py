"""
Sample Data Loader Script
Loads sample invoice data into the vector database for testing and demonstration
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.vector_store import VectorStoreManager
from app.core.embeddings import EmbeddingGenerator
from config import settings

class SampleDataLoader:
    """Loads sample invoice data for testing purposes"""
    
    def __init__(self):
        self.vector_store = VectorStoreManager(persist_directory=settings.vector_db_path)
        self.embedding_generator = EmbeddingGenerator()
    
    def generate_sample_invoices(self) -> list:
        """
        Generate realistic sample invoice data
        
        Returns:
            List of sample invoice dictionaries
        """
        
        # Sample employees
        employees = [
            "John Smith", "Sarah Johnson", "Mike Davis", "Emily Chen", 
            "David Brown", "Lisa Wilson", "Tom Anderson", "Maria Garcia"
        ]
        
        # Sample expense types and data
        expense_types = [
            {
                "type": "Business Meal",
                "amounts": [25.50, 45.00, 67.25, 89.50, 120.00],
                "vendors": ["Restaurant ABC", "Cafe Bistro", "Downtown Grill", "Business Center Cafe"],
                "reasons": [
                    "Client meeting lunch with potential customer",
                    "Team lunch during project planning session", 
                    "Business dinner with vendor representatives",
                    "Networking event meal with industry contacts"
                ]
            },
            {
                "type": "Transportation",
                "amounts": [15.75, 32.50, 48.00, 125.00, 200.00],
                "vendors": ["Uber", "Taxi Service", "Metro Transit", "Airport Shuttle"],
                "reasons": [
                    "Travel to client meeting downtown",
                    "Airport transportation for business trip",
                    "Daily commute during conference attendance",
                    "Transportation between multiple client sites"
                ]
            },
            {
                "type": "Office Supplies",
                "amounts": [12.99, 25.50, 45.75, 89.00, 156.25],
                "vendors": ["Office Depot", "Staples", "Amazon Business", "Local Office Supply"],
                "reasons": [
                    "Notebooks and pens for project documentation",
                    "Printer cartridges for quarterly reports",
                    "Presentation materials for client pitch",
                    "Desk organizers and filing supplies"
                ]
            },
            {
                "type": "Hotel Accommodation", 
                "amounts": [125.00, 189.50, 225.00, 275.00, 350.00],
                "vendors": ["Business Hotel", "Conference Center Hotel", "Downtown Inn", "Airport Hotel"],
                "reasons": [
                    "Overnight stay for multi-day client engagement",
                    "Conference attendance accommodation",
                    "Business trip lodging for vendor meetings",
                    "Training workshop hotel stay"
                ]
            }
        ]
        
        # Reimbursement statuses with probabilities
        statuses = [
            ("Fully Reimbursed", 0.7),
            ("Partially Reimbursed", 0.2), 
            ("Declined", 0.1)
        ]
        
        sample_invoices = []
        
        # Generate 50 sample invoices
        for i in range(50):
            # Random employee
            employee = random.choice(employees)
            
            # Random expense type
            expense = random.choice(expense_types)
            
            # Random amount from expense type
            amount = random.choice(expense["amounts"])
            
            # Random vendor and reason
            vendor = random.choice(expense["vendors"])
            reason_base = random.choice(expense["reasons"])
            
            # Random date in last 6 months
            days_ago = random.randint(1, 180)
            invoice_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            # Random status based on probabilities
            status_choice = random.random()
            cumulative_prob = 0
            selected_status = "Fully Reimbursed"
            
            for status, prob in statuses:
                cumulative_prob += prob
                if status_choice <= cumulative_prob:
                    selected_status = status
                    break
            
            # Adjust amounts based on status
            if selected_status == "Fully Reimbursed":
                reimbursable_amount = amount
                reason = f"Approved: {reason_base}"
            elif selected_status == "Partially Reimbursed":
                reimbursable_amount = round(amount * 0.7, 2)  # 70% reimbursed
                reason = f"Partial approval: {reason_base} - Some items exceed policy limits"
            else:  # Declined
                reimbursable_amount = 0.00
                reason = f"Declined: {reason_base} - Does not meet policy requirements"
            
            # Create invoice record
            invoice = {
                "invoice_id": f"INV_{i+1:03d}",
                "employee_name": employee,
                "file_name": f"invoice_{i+1:03d}.pdf",
                "status": selected_status,
                "reason": reason,
                "reimbursable_amount": str(reimbursable_amount),
                "total_amount": str(amount),
                "date": invoice_date,
                "vendor": vendor,
                "expense_type": expense["type"],
                "raw_text": f"""
INVOICE #{i+1:03d}
Date: {invoice_date}
Vendor: {vendor}
Employee: {employee}
Description: {expense['type']} - {reason_base}
Amount: ${amount}
Business Purpose: {reason_base}
"""
            }
            
            sample_invoices.append(invoice)
        
        return sample_invoices
    
    def load_sample_data(self, invoices: list) -> bool:
        """
        Load sample invoices into the vector database
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        
        print(f"📤 Loading {len(invoices)} sample invoices into vector database...")
        
        loaded_count = 0
        failed_count = 0
        
        for invoice in invoices:
            try:
                # Generate embedding for the invoice
                embedding_text = f"""
                Employee: {invoice['employee_name']}
                Expense Type: {invoice.get('expense_type', 'Unknown')}
                Status: {invoice['status']}
                Reason: {invoice['reason']}
                Amount: {invoice['total_amount']}
                Vendor: {invoice.get('vendor', 'Unknown')}
                {invoice.get('raw_text', '')}
                """
                
                embedding = self.embedding_generator.generate_embedding(embedding_text)
                
                # Add to vector store
                doc_id = self.vector_store.add_invoice(
                    invoice_data=invoice,
                    embedding=embedding
                )
                
                loaded_count += 1
                print(f"   ✅ Loaded: {invoice['invoice_id']} - {invoice['employee_name']}")
                
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Failed: {invoice['invoice_id']} - {str(e)}")
        
        print(f"\n📊 Loading Summary:")
        print(f"   Successfully loaded: {loaded_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Total: {len(invoices)}")
        
        return failed_count == 0
    
    def create_sample_files(self, output_dir: str = "./data/sample_data"):
        """
        Create sample data files for reference
        
        Args:
            output_dir: Directory to save sample files
        """
        
        print(f"📁 Creating sample data files in {output_dir}...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate sample data
        invoices = self.generate_sample_invoices()
        
        # Save as JSON
        with open(f"{output_dir}/sample_invoices.json", "w") as f:
            json.dump(invoices, f, indent=2)
        
        # Create summary statistics
        stats = self.generate_statistics(invoices)
        with open(f"{output_dir}/sample_statistics.json", "w") as f:
            json.dump(stats, f, indent=2)
        
        # Create sample queries
        queries = self.generate_sample_queries()
        with open(f"{output_dir}/sample_queries.txt", "w") as f:
            f.write("\n".join(queries))
        
        print(f"✅ Sample files created:")
        print(f"   - sample_invoices.json ({len(invoices)} invoices)")
        print(f"   - sample_statistics.json")
        print(f"   - sample_queries.txt ({len(queries)} queries)")
    
    def generate_statistics(self, invoices: list) -> dict:
        """Generate statistics about sample data"""
        
        total_invoices = len(invoices)
        total_amount = sum(float(inv['total_amount']) for inv in invoices)
        total_reimbursed = sum(float(inv['reimbursable_amount']) for inv in invoices)
        
        status_counts = {}
        employee_counts = {}
        expense_types = {}
        
        for invoice in invoices:
            # Status distribution
            status = invoice['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Employee distribution
            employee = invoice['employee_name']
            employee_counts[employee] = employee_counts.get(employee, 0) + 1
            
            # Expense type distribution
            expense_type = invoice.get('expense_type', 'Unknown')
            expense_types[expense_type] = expense_types.get(expense_type, 0) + 1
        
        return {
            "total_invoices": total_invoices,
            "total_amount": round(total_amount, 2),
            "total_reimbursed": round(total_reimbursed, 2),
            "reimbursement_rate": round((total_reimbursed / total_amount) * 100, 1),
            "status_distribution": status_counts,
            "employee_distribution": employee_counts,
            "expense_type_distribution": expense_types,
            "generated_date": datetime.now().isoformat()
        }
    
    def generate_sample_queries(self) -> list:
        """Generate sample queries for testing the chatbot"""
        
        return [
            "Show me all invoices for John Smith",
            "What invoices were declined last month?",
            "Find expenses over $100",
            "Show me all business meal expenses",
            "What's the total reimbursement amount for Sarah Johnson?",
            "Which employees have the most declined invoices?",
            "Show me all hotel accommodation expenses",
            "Find invoices from the last 30 days",
            "What are the most common reasons for declined expenses?",
            "Show me all transportation expenses for Mike Davis",
            "Find all invoices with partial reimbursement",
            "What's the average reimbursement amount?",
            "Show me office supply expenses",
            "Which vendor appears most frequently?",
            "Find all invoices submitted in January 2024"
        ]

def main():
    """Main function to run the sample data loader"""
    
    print("Sample Data Loader for Invoice Reimbursement System")
    print("=" * 55)
    
    loader = SampleDataLoader()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "load":
            # Generate and load sample data
            invoices = loader.generate_sample_invoices()
            loader.load_sample_data(invoices)
            
        elif command == "files":
            # Create sample files only
            loader.create_sample_files()
            
        elif command == "both":
            # Create files and load data
            invoices = loader.generate_sample_invoices()
            loader.create_sample_files()
            loader.load_sample_data(invoices)
            
        else:
            print(f"Unknown command: {command}")
            print("Available commands: load, files, both")
    else:
        print("Available options:")
        print("1. Load sample data into vector database")
        print("2. Create sample data files")
        print("3. Both")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            invoices = loader.generate_sample_invoices()
            loader.load_sample_data(invoices)
        elif choice == "2":
            loader.create_sample_files()
        elif choice == "3":
            invoices = loader.generate_sample_invoices()
            loader.create_sample_files()
            loader.load_sample_data(invoices)
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()