#!/usr/bin/env python3
"""
Train Llama Agent for "All Requests" Queries
============================================

This script specifically trains the Llama agent to handle queries that should
return all requests without any filters (empty quals array).
"""

import json
import requests
import time
from typing import Dict, List, Any

class AllRequestsTrainer:
    """Train the agent for all requests queries"""
    
    def __init__(self):
        self.api_endpoint = "http://127.0.0.1:5000"
    
    def generate_all_requests_training_examples(self) -> List[Dict[str, Any]]:
        """Generate training examples for all requests queries"""
        examples = []
        
        # Various ways users might ask for all requests
        all_requests_prompts = [
            "Give all request",
            "Get all requests", 
            "Show all requests",
            "Fetch all requests",
            "List all requests",
            "Display all requests",
            "Show me all requests",
            "Get me all requests",
            "Give me all requests",
            "Fetch me all requests",
            "I want all requests",
            "Show all the requests",
            "Get all the requests",
            "List all the requests",
            "Display all the requests",
            "Show me all the requests",
            "Get me all the requests",
            "Give me all the requests",
            "Fetch me all the requests",
            "I want all the requests",
            "Show requests",
            "Get requests",
            "List requests",
            "Display requests",
            "Show me requests",
            "Get me requests",
            "Give me requests",
            "Fetch me requests",
            "I want requests",
            "All requests",
            "All the requests",
            "Every request",
            "Every requests",
            "Complete list of requests",
            "Full list of requests",
            "Entire list of requests"
        ]
        
        # Expected JSON for all requests (empty quals)
        expected_json = {
            "qualDetails": {
                "type": "FlatQualificationRest",
                "quals": []
            }
        }
        
        # Create training examples
        for prompt in all_requests_prompts:
            examples.append({
                "prompt": prompt,
                "expected_json": expected_json,
                "description": f"All requests query: '{prompt}' should return empty quals array"
            })
        
        return examples
    
    def test_all_requests_query(self, prompt: str) -> Dict[str, Any]:
        """Test a single all requests query"""
        try:
            response = requests.post(
                f"{self.api_endpoint}/execute-request",
                headers={'Content-Type': 'application/json'},
                json={"request": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "prompt": prompt,
                    "total_count": result.get('total_count', 0),
                    "qualification": result.get('qualification', {}),
                    "quals_empty": len(result.get('qualification', {}).get('qualDetails', {}).get('quals', [])) == 0
                }
            else:
                return {
                    "success": False,
                    "prompt": prompt,
                    "error": f"HTTP {response.status_code}",
                    "quals_empty": False
                }
                
        except Exception as e:
            return {
                "success": False,
                "prompt": prompt,
                "error": str(e),
                "quals_empty": False
            }
    
    def train_all_requests_patterns(self) -> Dict[str, Any]:
        """Train the agent with all requests patterns"""
        print("🎓 Training agent for 'All Requests' queries...")
        print("=" * 50)
        
        # Generate training examples
        examples = self.generate_all_requests_training_examples()
        print(f"📚 Generated {len(examples)} training examples")
        
        successful_trainings = 0
        correct_empty_quals = 0
        total_examples = len(examples)
        
        print("\n🔄 Testing all requests patterns...")
        
        for i, example in enumerate(examples):
            prompt = example["prompt"]
            print(f"\n🧪 Testing {i+1}/{total_examples}: '{prompt}'")
            
            # Test the query
            result = self.test_all_requests_query(prompt)
            
            if result["success"]:
                successful_trainings += 1
                total_count = result["total_count"]
                
                if result["quals_empty"]:
                    correct_empty_quals += 1
                    print(f"   ✅ SUCCESS - Empty quals, found {total_count} requests")
                else:
                    quals = result["qualification"].get("qualDetails", {}).get("quals", [])
                    print(f"   ❌ INCORRECT - Has {len(quals)} filter(s), found {total_count} requests")
                    print(f"      Expected: Empty quals array")
                    print(f"      Got: {len(quals)} qualification(s)")
            else:
                print(f"   ❌ FAILED - {result['error']}")
            
            # Small delay between requests
            time.sleep(0.5)
        
        success_rate = successful_trainings / total_examples * 100
        correct_rate = correct_empty_quals / total_examples * 100
        
        print(f"\n🎯 Training Results:")
        print(f"   Total examples: {total_examples}")
        print(f"   Successful API calls: {successful_trainings}")
        print(f"   Correct empty quals: {correct_empty_quals}")
        print(f"   API success rate: {success_rate:.1f}%")
        print(f"   Correct quals rate: {correct_rate:.1f}%")
        
        return {
            'total_examples': total_examples,
            'successful_trainings': successful_trainings,
            'correct_empty_quals': correct_empty_quals,
            'api_success_rate': success_rate,
            'correct_quals_rate': correct_rate
        }
    
    def test_mixed_queries(self) -> None:
        """Test mixed queries to ensure specific filters still work"""
        print("\n🧪 Testing Mixed Queries (to ensure specific filters still work)...")
        print("=" * 60)
        
        mixed_queries = [
            {
                "prompt": "Get all requests",
                "expected_quals": 0,
                "description": "Should have empty quals"
            },
            {
                "prompt": "Get all requests with priority as high", 
                "expected_quals": 1,
                "description": "Should have priority filter"
            },
            {
                "prompt": "Show all requests",
                "expected_quals": 0,
                "description": "Should have empty quals"
            },
            {
                "prompt": "Get requests with status as open",
                "expected_quals": 1,
                "description": "Should have status filter"
            },
            {
                "prompt": "List all requests",
                "expected_quals": 0,
                "description": "Should have empty quals"
            }
        ]
        
        for query in mixed_queries:
            print(f"\n🔍 Testing: '{query['prompt']}'")
            result = self.test_all_requests_query(query["prompt"])
            
            if result["success"]:
                actual_quals = len(result["qualification"].get("qualDetails", {}).get("quals", []))
                expected_quals = query["expected_quals"]
                
                if actual_quals == expected_quals:
                    print(f"   ✅ CORRECT - {query['description']} ({actual_quals} quals)")
                else:
                    print(f"   ❌ INCORRECT - Expected {expected_quals} quals, got {actual_quals}")
                    print(f"      {query['description']}")
            else:
                print(f"   ❌ FAILED - {result['error']}")

def main():
    """Main training function"""
    print("🚀 All Requests Training System")
    print("=" * 40)
    
    trainer = AllRequestsTrainer()
    
    # Train all requests patterns
    results = trainer.train_all_requests_patterns()
    
    # Test mixed queries
    trainer.test_mixed_queries()
    
    print(f"\n🎉 Training completed!")
    print(f"   Correct empty quals rate: {results['correct_quals_rate']:.1f}%")
    
    if results['correct_quals_rate'] >= 90:
        print("✅ Training successful - Model correctly handles 'all requests' queries!")
    else:
        print("⚠️ Training needs improvement - Some queries still generate filters")

if __name__ == "__main__":
    main()
