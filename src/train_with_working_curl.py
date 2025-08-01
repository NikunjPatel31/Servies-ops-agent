#!/usr/bin/env python3
"""
Train Llama Agent with Working CURL Command
==========================================

This script trains the Llama agent using the working curl command and real data
from the ITSM API to ensure perfect compatibility.
"""

import json
import requests
import time
from typing import Dict, List, Any

class WorkingCurlTrainer:
    """Train the agent using working curl patterns"""
    
    def __init__(self):
        self.api_endpoint = "http://127.0.0.1:5000"
        self.working_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dpbl9zc29faWQiOjAsInVzZXJfbmFtZSI6InV1aWQzNi04OWRiOTc1My0zYTA5LTQzYTgtYTIzYS03ZjMwOGJkNDIyMWEiLCJzY29wZSI6WyJOTy1TQ09QRSJdLCJsb2dpbl9zb3VyY2UiOiJub3JtYWxfbG9naW4iLCJleHAiOjE3NTQyNDUxNTQsImxvZ2luX21zcF9wb3J0YWxfaWQiOjAsImp0aSI6ImU0OGE1Y2YwLTc0NzctNDkwYS1iMDAyLWFiNGU1Y2M2NzM2ZCIsImNsaWVudF9pZCI6ImZsb3RvLXdlYi1hcHAiLCJ0ZW5hbnRJZGVudGlmaWVyIjoiYXBvbG8ifQ.kS63w8cBY_wsHDV__X-EeKIJpeY5KekBDePduAAQdkk6uKFYu_MHnDFNs6X6qeYbu1E-2GNNPqyqaKbcAxtxEf98px2qWkU1WWWNjnYHCpQhFKakEK0X1b06CRXTbUHl2dRYUBzSk7VS49tesEMCBGYCD4NM33nc3fVQStNuedrqsiIEOqLk4GDGvtv41Lf2isKYRqgcilWcnLxhVq4Vgm1zHHDqUih9VH1W_Kcy3B0qcfm-u8INeI2I6E14Bb8Cluc7WaMvLbZyvte8HrsqvAH2NgSlOsWoFZ6BdhL0r82NQ_yKTKsHBY7sRwrW8GDl624xaExKTSKaWfMP1lAGQg"
        
        # Real data patterns from the working API response
        self.real_data_patterns = {
            "priority_values": {
                "low": 1,
                "medium": 2, 
                "high": 3,
                "critical": 4
            },
            "status_values": {
                "open": 9,
                "in_progress": 10,
                "pending": 11,
                "resolved": 12,
                "closed": 13
            },
            "real_subjects": [
                "printer issue",
                "Slow performance", 
                "Background Verification",
                "Data sync failed",
                "Request for admin portal access",
                "Unable to access API",
                "Suspicious mail",
                "Screen Freezes",
                "Request for new I-card",
                "Final Settlement Follow-up",
                "Connectivity Issue",
                "Salary slip not available"
            ]
        }
    
    def test_working_curl_directly(self) -> bool:
        """Test the working curl command directly"""
        print("🧪 Testing working curl command...")
        
        try:
            response = requests.post(
                'https://172.16.15.113/api/request/search/byqual?offset=0&size=25&sort_by=createdTime',
                headers={
                    'Accept': 'application/json, text/plain, */*',
                    'Authorization': f'Bearer {self.working_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                },
                json={"qualDetails":{"type":"FlatQualificationRest","quals":[]}},
                verify=False,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                total_count = data.get('totalCount', 0)
                print(f"✅ Working curl successful - Found {total_count} requests")
                return True
            else:
                print(f"❌ Working curl failed - Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Working curl error: {e}")
            return False
    
    def generate_training_examples_from_real_data(self) -> List[Dict[str, Any]]:
        """Generate training examples based on real API data patterns"""
        examples = []
        
        # Priority-based examples using real values
        priority_examples = [
            {
                "prompt": "Get all requests with priority as low",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.priorityId"
                            },
                            "operator": "Equal",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "LongValueRest",
                                    "value": 1
                                }
                            }
                        }]
                    }
                }
            },
            {
                "prompt": "Get all requests with priority as high",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.priorityId"
                            },
                            "operator": "Equal",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "LongValueRest",
                                    "value": 3
                                }
                            }
                        }]
                    }
                }
            }
        ]
        examples.extend(priority_examples)
        
        # Status-based examples using real values
        status_examples = [
            {
                "prompt": "Get all open requests",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.statusId"
                            },
                            "operator": "Equal",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "LongValueRest",
                                    "value": 9
                                }
                            }
                        }]
                    }
                }
            },
            {
                "prompt": "Get all requests in progress",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.statusId"
                            },
                            "operator": "Equal",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "LongValueRest",
                                    "value": 10
                                }
                            }
                        }]
                    }
                }
            }
        ]
        examples.extend(status_examples)
        
        # String search examples using real subjects
        string_examples = [
            {
                "prompt": "Find requests containing printer in subject",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.subject"
                            },
                            "operator": "Contains",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "StringValueRest",
                                    "value": "printer"
                                }
                            }
                        }]
                    }
                }
            },
            {
                "prompt": "Find requests with performance in subject",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.subject"
                            },
                            "operator": "Contains",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "StringValueRest",
                                    "value": "performance"
                                }
                            }
                        }]
                    }
                }
            }
        ]
        examples.extend(string_examples)
        
        return examples
    
    def train_agent_with_working_patterns(self) -> Dict[str, Any]:
        """Train the agent using working patterns"""
        print("🎓 Training agent with working curl patterns...")
        
        # Clear auth cache first
        try:
            requests.post(f"{self.api_endpoint}/auth/clear", timeout=10)
            print("🧹 Auth cache cleared")
        except:
            pass
        
        # Generate training examples
        examples = self.generate_training_examples_from_real_data()
        print(f"📚 Generated {len(examples)} training examples")
        
        successful_trainings = 0
        total_examples = len(examples)
        
        for i, example in enumerate(examples):
            try:
                print(f"\n🔄 Training example {i+1}/{total_examples}: '{example['prompt']}'")
                
                # Execute the training request
                response = requests.post(
                    f"{self.api_endpoint}/execute-request",
                    headers={'Content-Type': 'application/json'},
                    json={"request": example["prompt"]},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        successful_trainings += 1
                        total_count = result.get('total_count', 0)
                        print(f"   ✅ SUCCESS - Found {total_count} results")
                    else:
                        print(f"   ❌ FAILED - {result.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ HTTP ERROR - Status {response.status_code}")
                    
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ EXCEPTION - {e}")
        
        success_rate = successful_trainings / total_examples * 100
        print(f"\n🎯 Training completed!")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Successful: {successful_trainings}/{total_examples}")
        
        return {
            'total_examples': total_examples,
            'successful_trainings': successful_trainings,
            'success_rate': success_rate
        }

def main():
    """Main training function"""
    print("🚀 Working CURL Training System")
    print("=" * 40)
    
    trainer = WorkingCurlTrainer()
    
    # Test working curl first
    if not trainer.test_working_curl_directly():
        print("❌ Working curl test failed - cannot proceed")
        return
    
    # Train the agent
    results = trainer.train_agent_with_working_patterns()
    
    print(f"\n🎉 Training completed with {results['success_rate']:.1f}% success rate!")

if __name__ == "__main__":
    main()
