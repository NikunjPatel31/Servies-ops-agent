#!/usr/bin/env python3
"""
Comprehensive Test Suite for API Request Agent
Tests all cases from test-cases.pdf
"""

import requests
import json
import time
from typing import Dict, List, Tuple

class APITestSuite:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.endpoint = f"{base_url}/execute-request"
        
        # Test cases from test-cases.pdf
        self.test_cases = [
            {
                "prompt": "Get me all the request where assignee includes unassigned",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.technicianId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [0]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where Subject is Test",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.subject"
                                },
                                "operator": "contains",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "StringValueRest",
                                        "value": "test"
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where subject contains Test",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.subject"
                                },
                                "operator": "contains",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "StringValueRest",
                                        "value": "test"
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where subject has test inside",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.subject"
                                },
                                "operator": "contains",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "StringValueRest",
                                        "value": "test"
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where status is open",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.statusId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [9]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where status is in open state",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.statusId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [9]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where Status is in progress",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.statusId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [10]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where Status is in pending",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.statusId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [11]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where Status is in resolved",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.statusId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [12]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where Status is in Closed",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.statusId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [13]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where requester is AutoMinds",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.technicianId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [0]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "prompt": "Get me all the request where assignee has unassigned",
                "expected": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.technicianId"
                                },
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "ListLongValueRest",
                                        "value": [0]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ]
    
    def make_request(self, prompt: str) -> Dict:
        """Make API request"""
        try:
            response = requests.post(
                self.endpoint,
                json={"request": prompt},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            result = response.json()
            result['_status_code'] = response.status_code  # Add status code to result
            return result
        except Exception as e:
            return {"error": f"Request failed: {str(e)}", "_status_code": 0}
    
    def compare_qualifications(self, actual: Dict, expected: Dict) -> Tuple[bool, str]:
        """Compare actual vs expected qualifications"""
        try:
            # Extract qualification from actual response
            if 'qualification' in actual:
                actual_qual = actual['qualification']
            else:
                return False, "No qualification found in response"
            
            # Compare structure
            if actual_qual == expected:
                return True, "Perfect match"
            
            # Detailed comparison for debugging
            differences = []
            
            # Check type
            if actual_qual.get('qualDetails', {}).get('type') != expected.get('qualDetails', {}).get('type'):
                differences.append(f"Type mismatch: {actual_qual.get('qualDetails', {}).get('type')} vs {expected.get('qualDetails', {}).get('type')}")
            
            # Check quals count
            actual_quals = actual_qual.get('qualDetails', {}).get('quals', [])
            expected_quals = expected.get('qualDetails', {}).get('quals', [])
            
            if len(actual_quals) != len(expected_quals):
                differences.append(f"Quals count mismatch: {len(actual_quals)} vs {len(expected_quals)}")
            
            # Check first qual details if exists
            if actual_quals and expected_quals:
                actual_first = actual_quals[0]
                expected_first = expected_quals[0]
                
                if actual_first.get('type') != expected_first.get('type'):
                    differences.append(f"First qual type: {actual_first.get('type')} vs {expected_first.get('type')}")
                
                if actual_first.get('operator') != expected_first.get('operator'):
                    differences.append(f"Operator: {actual_first.get('operator')} vs {expected_first.get('operator')}")
                
                actual_key = actual_first.get('leftOperand', {}).get('key')
                expected_key = expected_first.get('leftOperand', {}).get('key')
                if actual_key != expected_key:
                    differences.append(f"Key: {actual_key} vs {expected_key}")
                
                actual_value = actual_first.get('rightOperand', {}).get('value', {}).get('value')
                expected_value = expected_first.get('rightOperand', {}).get('value', {}).get('value')
                if actual_value != expected_value:
                    differences.append(f"Value: {actual_value} vs {expected_value}")
            
            return False, "; ".join(differences) if differences else "Unknown difference"
            
        except Exception as e:
            return False, f"Comparison error: {str(e)}"

    def run_test_case(self, test_case: Dict, case_num: int) -> Dict:
        """Run a single test case"""
        prompt = test_case['prompt']
        expected = test_case['expected']

        print(f"\n🧪 Test Case {case_num}: {prompt}")

        # Make API request
        response = self.make_request(prompt)

        # Check status code first
        status_code = response.get('_status_code', 0)
        if status_code != 200:
            return {
                'case_num': case_num,
                'prompt': prompt,
                'status': 'ERROR',
                'error': f'HTTP {status_code}: Expected 200 status code',
                'expected': expected,
                'actual': response
            }

        # Check for qualification presence
        if 'qualification' not in response:
            return {
                'case_num': case_num,
                'prompt': prompt,
                'status': 'ERROR',
                'error': 'No qualification found in response',
                'expected': expected,
                'actual': response
            }

        # Compare qualifications
        is_match, details = self.compare_qualifications(response, expected)

        status = 'PASS' if is_match else 'FAIL'
        status_emoji = '✅' if is_match else '❌'

        print(f"   {status_emoji} {status}: {details}")

        return {
            'case_num': case_num,
            'prompt': prompt,
            'status': status,
            'details': details,
            'expected': expected,
            'actual': response.get('qualification', {}),
            'full_response': response
        }

    def run_all_tests(self) -> Dict:
        """Run all test cases"""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 80)

        results = []
        passed = 0
        failed = 0
        errors = 0

        for i, test_case in enumerate(self.test_cases, 1):
            result = self.run_test_case(test_case, i)
            results.append(result)

            if result['status'] == 'PASS':
                passed += 1
            elif result['status'] == 'FAIL':
                failed += 1
            else:
                errors += 1

            # Small delay between tests
            time.sleep(0.5)

        # Summary
        total = len(self.test_cases)
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔥 Errors: {errors}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        # Detailed failures
        if failed > 0 or errors > 0:
            print("\n🔍 DETAILED FAILURES:")
            print("-" * 80)
            for result in results:
                if result['status'] != 'PASS':
                    print(f"\n❌ Test {result['case_num']}: {result['prompt']}")
                    print(f"   Status: {result['status']}")
                    if 'error' in result:
                        print(f"   Error: {result['error']}")
                    else:
                        print(f"   Details: {result['details']}")

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'success_rate': (passed/total)*100,
            'results': results
        }

def main():
    """Main test execution"""
    print("🎯 API Request Agent - Comprehensive Test Suite")
    print("Testing all cases from test-cases.pdf")
    print("=" * 80)

    # Initialize test suite
    test_suite = APITestSuite()

    # Check if server is running
    try:
        health_response = requests.get(f"{test_suite.base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print("❌ Server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("Please ensure the server is running on http://localhost:5000")
        return

    # Run all tests
    summary = test_suite.run_all_tests()

    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n💾 Detailed results saved to test_results.json")

    # Exit with appropriate code
    if summary['failed'] == 0 and summary['errors'] == 0:
        print("🎉 All tests passed!")
        exit(0)
    else:
        print("⚠️ Some tests failed. Check the detailed output above.")
        exit(1)

if __name__ == "__main__":
    main()
