"""
Vector Database Setup Script
Initializes ChromaDB vector database for Invoice Reimbursement System
"""

import os
import sys
import chromadb
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from app.core.vector_store import VectorStoreManager
from app.core.embeddings import EmbeddingGenerator

def setup_vector_database():
    """
    Initialize and set up the vector database for the application
    """
    print("🚀 Setting up Vector Database for Invoice Reimbursement System")
    print("=" * 60)
    
    try:
        # Create vector database directory
        vector_db_path = settings.vector_db_path
        os.makedirs(vector_db_path, exist_ok=True)
        print(f"✅ Created vector database directory: {vector_db_path}")
        
        # Initialize vector store manager
        print("🔧 Initializing Vector Store Manager...")
        vector_store = VectorStoreManager(persist_directory=vector_db_path)
        print("✅ Vector Store Manager initialized successfully")
        
        # Initialize embedding generator
        print("🔧 Initializing Embedding Generator...")
        embedding_generator = EmbeddingGenerator()
        print(f"✅ Embedding Generator initialized with model: {embedding_generator.model_name}")
        
        # Get model information
        model_info = embedding_generator.get_model_info()
        print("\n📊 Embedding Model Information:")
        print(f"   Model Name: {model_info.get('model_name', 'Unknown')}")
        print(f"   Embedding Dimension: {model_info.get('embedding_dimension', 'Unknown')}")
        print(f"   Max Sequence Length: {model_info.get('max_seq_length', 'Unknown')}")
        
        # Test embedding generation
        print("\n🧪 Testing embedding generation...")
        test_text = "Sample invoice for business meal expense"
        test_embedding = embedding_generator.generate_embedding(test_text)
        print(f"✅ Test embedding generated successfully (dimension: {len(test_embedding)})")
        
        # Get collection statistics
        print("\n📈 Vector Database Statistics:")
        stats = vector_store.get_collection_stats()
        print(f"   Collection Name: {stats.get('collection_name', 'Unknown')}")
        print(f"   Document Count: {stats.get('document_count', 0)}")
        print(f"   Status: {stats.get('status', 'Unknown')}")
        
        # Test vector operations
        print("\n🧪 Testing vector database operations...")
        
        # Add a test document
        test_invoice_data = {
            "invoice_id": "test_001",
            "employee_name": "Test Employee",
            "status": "Fully Reimbursed",
            "reason": "Business meal within policy limits",
            "reimbursable_amount": "45.50",
            "date": "2024-01-15",
            "file_name": "test_invoice.pdf"
        }
        
        doc_id = vector_store.add_invoice(
            invoice_data=test_invoice_data,
            embedding=test_embedding
        )
        print(f"✅ Test document added with ID: {doc_id}")
        
        # Test search functionality
        search_results = vector_store.search_similar(
            query_embedding=test_embedding,
            n_results=1
        )
        print(f"✅ Search test successful (found {len(search_results)} results)")
        
        # Clean up test document
        vector_store.delete_invoice(doc_id)
        print("✅ Test document cleaned up")
        
        print("\n🎉 Vector Database Setup Complete!")
        print("\n📝 Next Steps:")
        print("1. Start your FastAPI application")
        print("2. Upload invoices through the /analyze-invoices endpoint")
        print("3. Query processed invoices using the /chat endpoint")
        print("4. Monitor the database using the statistics endpoints")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector Database Setup Failed: {str(e)}")
        return False

def reset_vector_database():
    """
    Reset the vector database by clearing all data
    """
    print("🔄 Resetting Vector Database...")
    
    try:
        vector_store = VectorStoreManager(persist_directory=settings.vector_db_path)
        
        # Clear the collection
        success = vector_store.clear_collection()
        
        if success:
            print("✅ Vector database reset successfully")
            
            # Verify reset
            stats = vector_store.get_collection_stats()
            print(f"📊 Current document count: {stats.get('document_count', 0)}")
        else:
            print("❌ Failed to reset vector database")
            
        return success
        
    except Exception as e:
        print(f"❌ Reset failed: {str(e)}")
        return False

def check_vector_database_health():
    """
    Check the health and status of the vector database
    """
    print("🏥 Checking Vector Database Health...")
    print("=" * 40)
    
    try:
        # Check if database directory exists
        if os.path.exists(settings.vector_db_path):
            print(f"✅ Database directory exists: {settings.vector_db_path}")
        else:
            print(f"❌ Database directory not found: {settings.vector_db_path}")
            return False
        
        # Initialize and check vector store
        vector_store = VectorStoreManager(persist_directory=settings.vector_db_path)
        stats = vector_store.get_collection_stats()
        
        print("📊 Database Statistics:")
        print(f"   Collection: {stats.get('collection_name', 'Unknown')}")
        print(f"   Documents: {stats.get('document_count', 0)}")
        print(f"   Status: {stats.get('status', 'Unknown')}")
        
        # Check embedding generator
        embedding_generator = EmbeddingGenerator()
        model_info = embedding_generator.get_model_info()
        
        print("\n🤖 Embedding Model Status:")
        print(f"   Model: {model_info.get('model_name', 'Unknown')}")
        print(f"   Dimension: {model_info.get('embedding_dimension', 'Unknown')}")
        
        # Test basic operations
        print("\n🧪 Testing Operations:")
        
        # Test embedding generation
        test_embedding = embedding_generator.generate_embedding("test")
        print(f"   ✅ Embedding generation: OK (dim: {len(test_embedding)})")
        
        # Test search
        search_results = vector_store.search_similar(test_embedding, n_results=1)
        print(f"   ✅ Vector search: OK (found {len(search_results)} results)")
        
        print("\n💚 Vector Database is healthy!")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Vector Database Management Script")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_vector_database()
        elif command == "reset":
            confirm = input("⚠️  Are you sure you want to reset the database? (y/N): ")
            if confirm.lower() == 'y':
                reset_vector_database()
            else:
                print("Reset cancelled")
        elif command == "health":
            check_vector_database_health()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: setup, reset, health")
    else:
        print("Available commands:")
        print("  python setup_vector_db.py setup  - Initialize vector database")
        print("  python setup_vector_db.py reset  - Reset database (delete all data)")
        print("  python setup_vector_db.py health - Check database health")
        
        choice = input("\nEnter command (setup/reset/health): ").strip().lower()
        
        if choice == "setup":
            setup_vector_database()
        elif choice == "reset":
            confirm = input("⚠️  Reset will delete all data. Continue? (y/N): ")
            if confirm.lower() == 'y':
                reset_vector_database()
        elif choice == "health":
            check_vector_database_health()
        else:
            print("Invalid choice")