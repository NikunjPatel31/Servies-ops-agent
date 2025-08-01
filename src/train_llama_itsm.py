#!/usr/bin/env python3
"""
Train Llama 3.8B with ITSM Documentation
========================================

This script trains the Llama model using comprehensive ITSM API documentation
to improve its understanding of qualification-based search patterns.
"""

import sys
import time
import requests
from itsm_training_system import ITSMTrainingSystem

def check_api_server(api_endpoint: str = "http://127.0.0.1:5000") -> bool:
    """Check if the API server is running"""
    try:
        response = requests.get(f"{api_endpoint}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return False

def check_ollama_status() -> bool:
    """Check if Ollama is running with Llama 3.8B"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_names = [model.get('name', '') for model in models.get('models', [])]
            if any('llama3:8b' in name for name in model_names):
                print("✅ Ollama is running with Llama 3.8B")
                return True
            else:
                print(f"❌ Llama 3.8B not found. Available models: {model_names}")
                return False
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def get_learning_statistics(api_endpoint: str = "http://127.0.0.1:5000") -> dict:
    """Get current learning statistics"""
    try:
        response = requests.get(f"{api_endpoint}/learning/statistics", timeout=10)
        if response.status_code == 200:
            return response.json().get('statistics', {})
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return {}

def main():
    """Main training function"""
    print("🎓 ITSM Training System for Llama 3.8B")
    print("=" * 50)
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    
    if not check_ollama_status():
        print("\n❌ Please start Ollama and ensure Llama 3.8B is available")
        print("   Run: ollama serve")
        print("   Run: ollama pull llama3:8b")
        sys.exit(1)
    
    if not check_api_server():
        print("\n❌ Please start the API server")
        print("   Run: cd src && python3 api_endpoint_server.py")
        sys.exit(1)
    
    # Initialize training system
    print("\n🚀 Initializing ITSM Training System...")
    trainer = ITSMTrainingSystem()
    
    # Get current learning statistics
    print("\n📊 Current Learning Statistics:")
    stats = get_learning_statistics()
    if stats:
        print(f"   Total interactions: {stats.get('total_interactions', 0)}")
        print(f"   Success rate: {stats.get('success_rate', 0)*100:.1f}%")
        print(f"   Recent interactions (7d): {stats.get('recent_interactions_7d', 0)}")
    
    # Ask user if they want to clear existing data
    print("\n🗑️ Learning Data Management:")
    clear_data = input("Clear existing learning data before training? (y/N): ").lower().strip()
    
    if clear_data in ['y', 'yes']:
        print("🧹 Clearing existing learning data...")
        if trainer.clear_learning_data():
            print("✅ Learning data cleared successfully")
        else:
            print("❌ Failed to clear learning data")
            sys.exit(1)
    
    # Start training
    print("\n🎓 Starting ITSM Documentation Training...")
    print("This will train Llama 3.8B with comprehensive ITSM API patterns")
    
    start_time = time.time()
    
    try:
        # Train with ITSM documentation examples
        results = trainer.train_llama_with_itsm_documentation()
        
        end_time = time.time()
        training_duration = end_time - start_time
        
        # Display results
        print("\n🎯 Training Results:")
        print(f"   Total examples: {results['total_examples']}")
        print(f"   Successful trainings: {results['successful_trainings']}")
        print(f"   Success rate: {results['success_rate']:.1f}%")
        print(f"   Training duration: {training_duration:.1f} seconds")
        
        # Get updated statistics
        print("\n📈 Updated Learning Statistics:")
        updated_stats = get_learning_statistics()
        if updated_stats:
            print(f"   Total interactions: {updated_stats.get('total_interactions', 0)}")
            print(f"   Success rate: {updated_stats.get('success_rate', 0)*100:.1f}%")
            print(f"   Recent interactions (7d): {updated_stats.get('recent_interactions_7d', 0)}")
        
        # Test the trained model
        print("\n🧪 Testing Trained Model:")
        test_queries = [
            "Get all requests with priority as high",
            "Find requests containing urgent in subject",
            "Show me open requests from requester 456",
            "Get requests without assigned technician"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/execute-request",
                    headers={'Content-Type': 'application/json'},
                    json={"request": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        total_count = result.get('total_count', 0)
                        print(f"   ✅ SUCCESS - Found {total_count} results")
                        
                        # Show qualification structure
                        qual = result.get('qualification', {})
                        if qual:
                            quals = qual.get('qualDetails', {}).get('quals', [])
                            print(f"   📋 Generated {len(quals)} filter(s)")
                    else:
                        print(f"   ❌ FAILED - {result.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ API ERROR - Status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ TEST ERROR - {e}")
        
        print("\n🎉 Training completed successfully!")
        print("\nThe Llama 3.8B model has been trained with comprehensive ITSM patterns.")
        print("It should now better understand qualification-based search structures.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
