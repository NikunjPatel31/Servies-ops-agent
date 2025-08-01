#!/usr/bin/env python3
"""
Training Data Generator for Dynamic Filter Creation
Generates comprehensive training examples for LLM-based filter generation
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class FilterTrainingDataGenerator:
    def __init__(self):
        # System mappings (these would come from your API)
        self.priority_mapping = {
            'low': 1, 'medium': 2, 'high': 3, 'critical': 4, 'urgent': 4,
            'p1': 4, 'p2': 3, 'p3': 2, 'p4': 1
        }
        
        self.status_mapping = {
            'open': 9, 'in progress': 10, 'pending': 11, 'resolved': 12, 
            'closed': 13, 'testing': 97, 'on hold': 98, 'cancelled': 99
        }
        
        self.urgency_mapping = {
            'low': 1, 'medium': 2, 'high': 3, 'critical': 4
        }
        
        # Sample data for realistic training
        self.users = {
            'john': 45, 'jane': 78, 'bob': 23, 'alice': 56, 'mike': 89
        }
        
        self.locations = {
            'new york': 10, 'london': 15, 'tokyo': 20, 'sydney': 25, 'berlin': 30
        }
        
        self.categories = {
            'it': 5, 'hr': 7, 'facilities': 9, 'finance': 11, 'security': 13
        }

    def generate_single_field_examples(self) -> List[Dict]:
        """Generate examples for single field filters"""
        examples = []
        
        # Priority examples
        priority_prompts = [
            ("Show high priority tickets", [3]),
            ("Find critical issues", [4]),
            ("Get P1 and P2 tickets", [4, 3]),
            ("Display medium or low priority items", [2, 1]),
            ("Show non-critical tickets", [1, 2, 3]),  # not_in [4]
            ("Find urgent requests", [4]),
        ]
        
        for prompt, values in priority_prompts:
            operator = "not_in" if "non-" in prompt else "in"
            if operator == "not_in":
                values = [4]  # Exclude critical
            
            examples.append({
                "prompt": prompt,
                "payload": {
                    "qualDetails": {
                        "quals": [{
                            "leftOperand": {"key": "request.priorityId", "type": "PropertyOperandRest"},
                            "operator": operator,
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {"type": "ListLongValueRest", "value": values}
                            }
                        }]
                    }
                },
                "field_type": "priority",
                "explanation": f"Priority filter: {operator} {values}"
            })
        
        # Status examples
        status_prompts = [
            ("Show open tickets", [9]),
            ("Find closed and resolved items", [13, 12]),
            ("Get in-progress requests", [10]),
            ("Display pending tickets", [11]),
            ("Show non-closed tickets", [9, 10, 11, 97, 98]),  # not_in [13]
        ]
        
        for prompt, values in status_prompts:
            operator = "not_in" if "non-" in prompt else "in"
            if operator == "not_in":
                values = [13]  # Exclude closed
            
            examples.append({
                "prompt": prompt,
                "payload": {
                    "qualDetails": {
                        "quals": [{
                            "leftOperand": {"key": "request.statusId", "type": "PropertyOperandRest"},
                            "operator": operator,
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {"type": "ListLongValueRest", "value": values}
                            }
                        }]
                    }
                },
                "field_type": "status",
                "explanation": f"Status filter: {operator} {values}"
            })
        
        return examples

    def generate_time_based_examples(self) -> List[Dict]:
        """Generate time-based filter examples"""
        examples = []
        
        time_prompts = [
            ("Show tickets created today", "within_last", 1, "days"),
            ("Find requests from last week", "within_last", 7, "days"),
            ("Get tickets from last month", "within_last", 30, "days"),
            ("Display items created yesterday", "within_last", 1, "days"),
            ("Show tickets older than 30 days", "before", 30, "days"),
        ]
        
        for prompt, operator, value, unit in time_prompts:
            if operator == "within_last":
                payload = {
                    "qualDetails": {
                        "quals": [{
                            "leftOperand": {"key": "created_date", "type": "VariableOperandRest"},
                            "operator": operator,
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {"type": "DurationValueRest", "value": value, "unit": unit}
                            }
                        }]
                    }
                }
            else:  # before
                date_str = (datetime.now() - timedelta(days=value)).strftime("%Y-%m-%dT00:00:00Z")
                payload = {
                    "qualDetails": {
                        "quals": [{
                            "leftOperand": {"key": "created_date", "type": "VariableOperandRest"},
                            "operator": operator,
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {"type": "DateValueRest", "value": date_str}
                            }
                        }]
                    }
                }
            
            examples.append({
                "prompt": prompt,
                "payload": payload,
                "field_type": "time",
                "explanation": f"Time filter: {operator} {value} {unit}"
            })
        
        return examples

    def generate_combination_examples(self) -> List[Dict]:
        """Generate complex combination filter examples"""
        examples = []
        
        combination_prompts = [
            {
                "prompt": "Show high priority open tickets",
                "filters": [
                    {"field": "priority", "values": [3]},
                    {"field": "status", "values": [9]}
                ]
            },
            {
                "prompt": "Find critical bugs from IT department",
                "filters": [
                    {"field": "priority", "values": [4]},
                    {"field": "category", "values": [5]}
                ]
            },
            {
                "prompt": "Get medium priority tickets assigned to John",
                "filters": [
                    {"field": "priority", "values": [2]},
                    {"field": "assignee", "values": [45]}
                ]
            },
            {
                "prompt": "Show resolved tickets from New York office",
                "filters": [
                    {"field": "status", "values": [12]},
                    {"field": "location", "values": [10]}
                ]
            }
        ]
        
        for item in combination_prompts:
            quals = []
            
            for filter_def in item["filters"]:
                field_map = {
                    "priority": "request.priorityId",
                    "status": "request.statusId",
                    "category": "request.categoryId",
                    "assignee": "request.technicianId",
                    "location": "request.locationId"
                }
                
                quals.append({
                    "leftOperand": {"key": field_map[filter_def["field"]], "type": "PropertyOperandRest"},
                    "operator": "in",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "ListLongValueRest", "value": filter_def["values"]}
                    }
                })
            
            examples.append({
                "prompt": item["prompt"],
                "payload": {"qualDetails": {"quals": quals}},
                "field_type": "combination",
                "explanation": f"Multi-field filter with {len(quals)} conditions"
            })
        
        return examples

    def generate_natural_language_variations(self) -> List[Dict]:
        """Generate natural language variations"""
        examples = []
        
        variations = [
            ("Could you show me all the high priority stuff?", [3], "priority"),
            ("I need to see what's open right now", [9], "status"),
            ("What tickets are assigned to me?", "CURRENT_USER", "assignee"),
            ("Show me everything that's not closed", [9, 10, 11, 97, 98], "status"),
            ("Find the critical issues we have", [4], "priority"),
            ("What's pending approval?", [11], "status"),
            ("Give me the IT tickets", [5], "category"),
        ]
        
        for prompt, values, field_type in variations:
            field_map = {
                "priority": "request.priorityId",
                "status": "request.statusId",
                "category": "request.categoryId",
                "assignee": "request.technicianId"
            }
            
            if values == "CURRENT_USER":
                # This would be resolved at runtime
                continue
            
            operator = "not_in" if "not closed" in prompt else "in"
            if operator == "not_in":
                values = [13]  # Exclude closed
            
            examples.append({
                "prompt": prompt,
                "payload": {
                    "qualDetails": {
                        "quals": [{
                            "leftOperand": {"key": field_map[field_type], "type": "PropertyOperandRest"},
                            "operator": operator,
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {"type": "ListLongValueRest", "value": values}
                            }
                        }]
                    }
                },
                "field_type": field_type,
                "explanation": f"Natural language: {field_type} filter"
            })
        
        return examples

    def generate_training_dataset(self, num_examples: int = 1000) -> Dict:
        """Generate complete training dataset"""
        all_examples = []
        
        # Generate different types of examples
        all_examples.extend(self.generate_single_field_examples())
        all_examples.extend(self.generate_time_based_examples())
        all_examples.extend(self.generate_combination_examples())
        all_examples.extend(self.generate_natural_language_variations())
        
        # Add more synthetic examples to reach target count
        while len(all_examples) < num_examples:
            # Generate random combinations
            all_examples.extend(self._generate_synthetic_examples(50))
        
        return {
            "metadata": {
                "total_examples": len(all_examples),
                "generated_at": datetime.now().isoformat(),
                "field_mappings": {
                    "priority": self.priority_mapping,
                    "status": self.status_mapping,
                    "urgency": self.urgency_mapping,
                    "users": self.users,
                    "locations": self.locations,
                    "categories": self.categories
                }
            },
            "examples": all_examples[:num_examples]
        }

    def _generate_synthetic_examples(self, count: int) -> List[Dict]:
        """Generate synthetic training examples"""
        examples = []
        
        templates = [
            "Show {priority} priority {status} tickets",
            "Find {category} requests from {location}",
            "Get tickets assigned to {user}",
            "Display {status} items with {priority} priority",
        ]
        
        for _ in range(count):
            template = random.choice(templates)
            
            # Fill template with random values
            filled = template.format(
                priority=random.choice(list(self.priority_mapping.keys())),
                status=random.choice(list(self.status_mapping.keys())),
                category=random.choice(list(self.categories.keys())),
                location=random.choice(list(self.locations.keys())),
                user=random.choice(list(self.users.keys()))
            )
            
            # Generate corresponding payload (simplified)
            examples.append({
                "prompt": filled,
                "payload": {"qualDetails": {"quals": []}},  # Would be filled properly
                "field_type": "synthetic",
                "explanation": "Synthetic training example"
            })
        
        return examples

if __name__ == "__main__":
    generator = FilterTrainingDataGenerator()
    dataset = generator.generate_training_dataset(500)
    
    with open("training_data.json", "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Generated {len(dataset['examples'])} training examples")
    print("Saved to training_data.json")
