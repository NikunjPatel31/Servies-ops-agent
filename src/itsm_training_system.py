#!/usr/bin/env python3
"""
ITSM Training System for Llama 3.8B
===================================

This module trains the Llama model using the comprehensive ITSM API documentation
to understand qualification-based search patterns and generate accurate API calls.
"""

import json
import re
import random
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import requests

class ITSMTrainingSystem:
    """
    Comprehensive training system for ITSM API qualification generation
    """
    
    def __init__(self, llama_endpoint: str = "http://localhost:11434/api/generate"):
        self.llama_endpoint = llama_endpoint
        self.training_examples = []
        self.field_mappings = {
            'status': 'request.statusId',
            'priority': 'request.priorityId', 
            'urgency': 'request.urgencyId',
            'impact': 'request.impactId',
            'requester': 'request.requesterId',
            'technician': 'request.technicianId',
            'assignee': 'request.technicianId',
            'group': 'request.groupId',
            'category': 'request.categoryId',
            'subcategory': 'request.subCategoryId',
            'subject': 'request.subject',
            'description': 'request.description',
            'name': 'request.name',
            'tags': 'request.tags',
            'created': 'request.createdTime',
            'updated': 'request.updatedTime',
            'due': 'request.dueByTime'
        }
        
        self.operators = {
            'equals': 'Equal',
            'is': 'Equal',
            'not equals': 'Not_Equal',
            'not': 'Not_Equal',
            'contains': 'Contains',
            'includes': 'Contains',
            'has': 'Contains',
            'not contains': 'Not_Contains',
            'starts with': 'Start_With',
            'begins with': 'Start_With',
            'ends with': 'End_With',
            'in': 'In',
            'not in': 'Not_In',
            'greater than': 'GreaterThan',
            'less than': 'LessThan',
            'before': 'Before',
            'after': 'After',
            'between': 'Between'
        }
        
        self.value_types = {
            'string': 'StringValueRest',
            'number': 'LongValueRest',
            'integer': 'IntegerValueRest',
            'boolean': 'BooleanValueRest',
            'list_string': 'ListStringValueRest',
            'list_number': 'ListLongValueRest',
            'time': 'TimeValueRest'
        }
        
        print("🎓 ITSM Training System initialized")
    
    def generate_comprehensive_training_examples(self) -> List[Dict]:
        """Generate comprehensive training examples from ITSM documentation"""
        examples = []
        
        # 1. Basic field filtering examples
        examples.extend(self._generate_basic_field_examples())
        
        # 2. String operation examples
        examples.extend(self._generate_string_operation_examples())
        
        # 3. List and multiple value examples
        examples.extend(self._generate_list_operation_examples())
        
        # 4. Date and time examples
        examples.extend(self._generate_date_time_examples())
        
        # 5. Complex combination examples
        examples.extend(self._generate_complex_combination_examples())
        
        # 6. Null check examples
        examples.extend(self._generate_null_check_examples())
        
        # 7. Tag-based examples
        examples.extend(self._generate_tag_examples())
        
        # 8. Natural language variations
        examples.extend(self._generate_natural_language_variations())
        
        self.training_examples = examples
        print(f"📚 Generated {len(examples)} comprehensive training examples")
        return examples
    
    def _generate_basic_field_examples(self) -> List[Dict]:
        """Generate basic field filtering examples"""
        examples = []
        
        # Status examples
        status_examples = [
            ("Get all open requests", "request.statusId", "In", [9]),
            ("Show me closed requests", "request.statusId", "Equal", 13),
            ("Find requests that are not closed", "request.statusId", "Not_Equal", 13),
            ("Get requests with status in progress", "request.statusId", "Equal", 10)
        ]
        
        # Priority examples  
        priority_examples = [
            ("Get high priority requests", "request.priorityId", "Equal", 3),
            ("Show me low priority tickets", "request.priorityId", "Equal", 1),
            ("Find medium priority requests", "request.priorityId", "Equal", 2),
            ("Get requests with priority not high", "request.priorityId", "Not_Equal", 3)
        ]
        
        # Urgency examples
        urgency_examples = [
            ("Get urgent requests", "request.urgencyId", "Equal", 3),
            ("Show me low urgency tickets", "request.urgencyId", "Equal", 1),
            ("Find high urgency requests", "request.urgencyId", "Equal", 3)
        ]
        
        for prompt, field, operator, value in status_examples + priority_examples + urgency_examples:
            examples.append(self._create_training_example(prompt, field, operator, value))
        
        return examples
    
    def _generate_string_operation_examples(self) -> List[Dict]:
        """Generate string operation examples"""
        examples = []
        
        string_examples = [
            ("Find requests containing 'urgent' in subject", "request.subject", "Contains", "urgent"),
            ("Get requests with subject starting with 'INC'", "request.subject", "Start_With", "INC"),
            ("Show requests ending with 'resolved'", "request.subject", "End_With", "resolved"),
            ("Find requests with description containing 'error'", "request.description", "Contains", "error"),
            ("Get requests where name contains 'network'", "request.name", "Contains", "network")
        ]
        
        for prompt, field, operator, value in string_examples:
            examples.append(self._create_training_example(prompt, field, operator, value, value_type="string"))
        
        return examples
    
    def _generate_list_operation_examples(self) -> List[Dict]:
        """Generate list and multiple value examples"""
        examples = []
        
        list_examples = [
            ("Get requests with status open or in progress", "request.statusId", "In", [9, 10]),
            ("Find requests with high or medium priority", "request.priorityId", "In", [2, 3]),
            ("Show requests not in closed or resolved status", "request.statusId", "Not_In", [12, 13]),
            ("Get requests with priority 1, 2, or 3", "request.priorityId", "In", [1, 2, 3])
        ]
        
        for prompt, field, operator, value in list_examples:
            examples.append(self._create_training_example(prompt, field, operator, value, value_type="list_number"))
        
        return examples
    
    def _create_training_example(self, prompt: str, field: str, operator: str, value: Any, value_type: str = "number") -> Dict:
        """Create a training example with proper ITSM API structure"""
        
        # Determine value structure based on type
        if value_type == "string":
            value_obj = {
                "type": "StringValueRest",
                "value": value
            }
        elif value_type == "list_number":
            value_obj = {
                "type": "ListLongValueRest", 
                "value": value
            }
        elif value_type == "list_string":
            value_obj = {
                "type": "ListStringValueRest",
                "value": value
            }
        else:  # number/integer
            value_obj = {
                "type": "LongValueRest",
                "value": value
            }
        
        # Create the complete qualification structure
        qualification = {
            "qualDetails": {
                "type": "FlatQualificationRest",
                "quals": [{
                    "type": "RelationalQualificationRest",
                    "leftOperand": {
                        "type": "PropertyOperandRest",
                        "key": field
                    },
                    "operator": operator,
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": value_obj
                    }
                }]
            }
        }
        
        return {
            "prompt": prompt,
            "qualification": qualification,
            "field": field,
            "operator": operator,
            "value": value,
            "value_type": value_type
        }
    
    def _generate_date_time_examples(self) -> List[Dict]:
        """Generate date and time filtering examples"""
        examples = []
        
        # Note: These would need actual date values in real implementation
        date_examples = [
            ("Get requests created today", "request.createdTime", "Equal", "today"),
            ("Find requests created this week", "request.createdTime", "GreaterThanOrEqual", "this_week"),
            ("Show requests updated yesterday", "request.updatedTime", "Equal", "yesterday"),
            ("Get requests due before tomorrow", "request.dueByTime", "Before", "tomorrow")
        ]
        
        for prompt, field, operator, value in date_examples:
            examples.append(self._create_training_example(prompt, field, operator, value, value_type="string"))
        
        return examples
    
    def _generate_complex_combination_examples(self) -> List[Dict]:
        """Generate complex combination examples with multiple conditions"""
        examples = []
        
        # These would create more complex qualification structures
        # For now, keeping simpler examples that can be extended
        
        return examples
    
    def _generate_null_check_examples(self) -> List[Dict]:
        """Generate null check examples"""
        examples = []
        
        # Null check examples would use UnaryQualificationRest
        # Simplified for now
        
        return examples
    
    def _generate_tag_examples(self) -> List[Dict]:
        """Generate tag-based filtering examples"""
        examples = []
        
        tag_examples = [
            ("Find requests tagged with 'urgent'", "request.tags", "All_Members_Exist", ["urgent"]),
            ("Get requests with tags 'hardware' and 'network'", "request.tags", "All_Members_Exist", ["hardware", "network"]),
            ("Show requests tagged with 'critical'", "request.tags", "Contains", "critical")
        ]
        
        for prompt, field, operator, value in tag_examples:
            value_type = "list_string" if isinstance(value, list) else "string"
            examples.append(self._create_training_example(prompt, field, operator, value, value_type=value_type))
        
        return examples
    
    def _generate_natural_language_variations(self) -> List[Dict]:
        """Generate natural language variations of the same queries"""
        examples = []
        
        # Variations for the same logical query
        base_queries = [
            ("Get high priority requests", "request.priorityId", "Equal", 3),
            ("Show me open tickets", "request.statusId", "Equal", 9),
            ("Find urgent requests", "request.urgencyId", "Equal", 3)
        ]
        
        variations = [
            "Get all {}", "Show me {}", "Find {}", "List {}", "Display {}",
            "I need {}", "Can you get {}", "Please show {}", "Retrieve {}"
        ]
        
        for base_prompt, field, operator, value in base_queries:
            # Extract the main part (e.g., "high priority requests")
            main_part = base_prompt.split(" ", 1)[1] if " " in base_prompt else base_prompt
            
            for variation in variations:
                new_prompt = variation.format(main_part)
                examples.append(self._create_training_example(new_prompt, field, operator, value))
        
        return examples

    def train_llama_with_itsm_documentation(self, api_endpoint: str = "http://127.0.0.1:5000"):
        """Train Llama using comprehensive ITSM documentation examples"""
        print("🎓 Starting comprehensive ITSM training based on documentation...")

        # Generate all training examples
        training_examples = self.generate_itsm_documentation_examples()

        # Add to existing examples
        training_examples.extend(self.generate_comprehensive_training_examples())

        print(f"📚 Generated {len(training_examples)} training examples")

        # Train through API calls
        successful_trainings = 0
        total_examples = len(training_examples)

        for i, example in enumerate(training_examples):
            try:
                # Make API call to train the model
                response = self._execute_training_request(api_endpoint, example)

                if response and response.get('success'):
                    successful_trainings += 1
                    print(f"✅ Training example {i+1}/{total_examples}: SUCCESS")
                else:
                    print(f"❌ Training example {i+1}/{total_examples}: FAILED")

                # Progress update every 10 examples
                if (i + 1) % 10 == 0:
                    success_rate = successful_trainings / (i + 1) * 100
                    print(f"📊 Progress: {i+1}/{total_examples} - Success rate: {success_rate:.1f}%")

            except Exception as e:
                print(f"⚠️ Training example {i+1} failed: {e}")

        final_success_rate = successful_trainings / total_examples * 100
        print(f"🎯 Training completed! Success rate: {final_success_rate:.1f}%")

        return {
            'total_examples': total_examples,
            'successful_trainings': successful_trainings,
            'success_rate': final_success_rate
        }

    def generate_itsm_documentation_examples(self) -> List[Dict[str, Any]]:
        """Generate training examples based on ITSM documentation patterns"""
        examples = []

        # 1. Simple Status Filtering (from doc example 1)
        examples.extend([
            {
                "prompt": "Get all requests except closed and resolved",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.statusId"
                            },
                            "operator": "Not_In",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "ListLongValueRest",
                                    "value": [13, 12]
                                }
                            }
                        }]
                    }
                }
            },
            {
                "prompt": "Show me requests that are not closed",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.statusId"
                            },
                            "operator": "Not_In",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "ListLongValueRest",
                                    "value": [13]
                                }
                            }
                        }]
                    }
                }
            }
        ])

        # 2. String Contains Search (from doc example 2)
        examples.extend([
            {
                "prompt": "Find requests with urgent in subject",
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
                                    "value": "urgent"
                                }
                            }
                        }]
                    }
                }
            },
            {
                "prompt": "Get requests containing error in description",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.description"
                            },
                            "operator": "Contains",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "StringValueRest",
                                    "value": "error"
                                }
                            }
                        }]
                    }
                }
            }
        ])

        # 3. Multiple Conditions (AND Logic) - from doc example 3
        examples.extend([
            {
                "prompt": "Get open requests from requester 456",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [
                            {
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
                            },
                            {
                                "type": "RelationalQualificationRest",
                                "leftOperand": {
                                    "type": "PropertyOperandRest",
                                    "key": "request.requesterId"
                                },
                                "operator": "Equal",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {
                                        "type": "LongValueRest",
                                        "value": 456
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ])

        # 4. OR Logic with Binary Qualification - from doc example 4
        examples.extend([
            {
                "prompt": "Get high priority or critical urgency requests",
                "expected_json": {
                    "qualDetails": {
                        "type": "BinaryQualificationRest",
                        "leftQual": {
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
                        },
                        "operator": "OR",
                        "rightQual": {
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.urgencyId"
                            },
                            "operator": "Equal",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "LongValueRest",
                                    "value": 4
                                }
                            }
                        }
                    }
                }
            }
        ])

        # 5. Null Check with Unary Qualification - from doc example 5
        examples.extend([
            {
                "prompt": "Find requests without assigned technician",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "UnaryQualificationRest",
                            "operand": {
                                "type": "PropertyOperandRest",
                                "key": "request.technicianId"
                            },
                            "operator": "Is_Null"
                        }]
                    }
                }
            },
            {
                "prompt": "Get unassigned requests",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "UnaryQualificationRest",
                            "operand": {
                                "type": "PropertyOperandRest",
                                "key": "request.technicianId"
                            },
                            "operator": "Is_Null"
                        }]
                    }
                }
            }
        ])

        # 6. Tag-Based Filtering - from doc example 8
        examples.extend([
            {
                "prompt": "Find requests tagged with urgent and hardware",
                "expected_json": {
                    "qualDetails": {
                        "type": "FlatQualificationRest",
                        "quals": [{
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": "request.tags"
                            },
                            "operator": "All_Members_Exist",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "ListStringValueRest",
                                    "value": ["urgent", "hardware"]
                                }
                            }
                        }]
                    }
                }
            }
        ])

        return examples

    def _execute_training_request(self, api_endpoint: str, example: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a training request through the API"""
        try:
            response = requests.post(
                f"{api_endpoint}/execute-request",
                headers={'Content-Type': 'application/json'},
                json={"request": example["prompt"]},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API call failed: {response.status_code}")
                return {"success": False}

        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {"success": False}

    def clear_learning_data(self, api_endpoint: str = "http://127.0.0.1:5000") -> bool:
        """Clear all learning data before training"""
        try:
            response = requests.post(
                f"{api_endpoint}/learning/clear",
                headers={'Content-Type': 'application/json'},
                json={"confirm": True},
                timeout=10
            )

            if response.status_code == 200:
                print("🗑️ Learning data cleared successfully")
                return True
            else:
                print(f"❌ Failed to clear learning data: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error clearing learning data: {e}")
            return False
