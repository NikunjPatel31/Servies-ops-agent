#!/usr/bin/env python3
"""
Generate comprehensive training data for LLM fine-tuning
Creates thousands of prompt-payload pairs for all filter combinations
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class TrainingDataGenerator:
    def __init__(self):
        # System mappings
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
        
        # Sample entities
        self.users = ['john', 'jane', 'bob', 'alice', 'mike', 'sarah', 'tom', 'lisa']
        self.locations = ['new york', 'london', 'tokyo', 'sydney', 'berlin', 'paris']
        self.categories = ['it', 'hr', 'facilities', 'finance', 'security', 'legal']

    def generate_comprehensive_dataset(self, total_examples: int = 2000) -> Dict:
        """Generate comprehensive training dataset"""
        examples = []
        
        # 1. Single field filters (400 examples)
        examples.extend(self._generate_priority_examples(100))
        examples.extend(self._generate_status_examples(100))
        examples.extend(self._generate_time_examples(100))
        examples.extend(self._generate_text_examples(100))
        
        # 2. Multi-field combinations (600 examples)
        examples.extend(self._generate_combination_examples(600))
        
        # 3. Natural language variations (500 examples)
        examples.extend(self._generate_natural_language_examples(500))
        
        # 4. Edge cases and negations (300 examples)
        examples.extend(self._generate_edge_cases(300))
        
        # 5. Complex scenarios (200 examples)
        examples.extend(self._generate_complex_scenarios(200))
        
        # Shuffle and limit to target count
        random.shuffle(examples)
        examples = examples[:total_examples]
        
        return {
            "metadata": {
                "total_examples": len(examples),
                "generated_at": datetime.now().isoformat(),
                "categories": {
                    "single_field": 400,
                    "combinations": 600,
                    "natural_language": 500,
                    "edge_cases": 300,
                    "complex": 200
                }
            },
            "examples": examples
        }

    def _generate_priority_examples(self, count: int) -> List[Dict]:
        """Generate priority-focused examples"""
        examples = []
        
        templates = [
            ("Show {priority} priority tickets", "single"),
            ("Find {priority} and {priority2} priority items", "multiple"),
            ("Get P{num} tickets", "p_notation"),
            ("Display non-{priority} priority requests", "negation"),
            ("Show tickets with {priority} priority", "with_syntax"),
        ]
        
        for i in range(count):
            template, example_type = random.choice(templates)
            
            if example_type == "single":
                priority = random.choice(list(self.priority_mapping.keys()))
                prompt = template.format(priority=priority)
                payload = self._create_priority_payload([self.priority_mapping[priority]])
                
            elif example_type == "multiple":
                priorities = random.sample(list(self.priority_mapping.keys()), 2)
                prompt = template.format(priority=priorities[0], priority2=priorities[1])
                values = [self.priority_mapping[p] for p in priorities]
                payload = self._create_priority_payload(values)
                
            elif example_type == "p_notation":
                p_num = random.choice([1, 2, 3, 4])
                prompt = template.format(num=p_num)
                priority_value = 5 - p_num  # P1=4, P2=3, P3=2, P4=1
                payload = self._create_priority_payload([priority_value])
                
            elif example_type == "negation":
                priority = random.choice(['critical', 'high', 'low'])
                prompt = template.format(priority=priority)
                excluded_value = self.priority_mapping[priority]
                all_values = list(self.priority_mapping.values())
                included_values = [v for v in all_values if v != excluded_value]
                payload = self._create_priority_payload(included_values, operator="not_in", excluded=[excluded_value])
                
            else:  # with_syntax
                priority = random.choice(list(self.priority_mapping.keys()))
                prompt = template.format(priority=priority)
                payload = self._create_priority_payload([self.priority_mapping[priority]])
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps(payload),
                "field_type": "priority",
                "example_type": example_type
            })
        
        return examples

    def _generate_status_examples(self, count: int) -> List[Dict]:
        """Generate status-focused examples"""
        examples = []
        
        templates = [
            ("Show {status} tickets", "single"),
            ("Find {status} and {status2} requests", "multiple"),
            ("Get tickets that are {status}", "are_syntax"),
            ("Display non-{status} items", "negation"),
            ("Show tickets in {status} status", "in_status"),
        ]
        
        for i in range(count):
            template, example_type = random.choice(templates)
            
            if example_type == "single":
                status = random.choice(list(self.status_mapping.keys()))
                prompt = template.format(status=status)
                payload = self._create_status_payload([self.status_mapping[status]])
                
            elif example_type == "multiple":
                statuses = random.sample(list(self.status_mapping.keys()), 2)
                prompt = template.format(status=statuses[0], status2=statuses[1])
                values = [self.status_mapping[s] for s in statuses]
                payload = self._create_status_payload(values)
                
            elif example_type == "negation":
                status = random.choice(['closed', 'cancelled'])
                prompt = template.format(status=status)
                excluded_value = self.status_mapping[status]
                all_values = list(self.status_mapping.values())
                included_values = [v for v in all_values if v != excluded_value]
                payload = self._create_status_payload(included_values, operator="not_in", excluded=[excluded_value])
                
            else:
                status = random.choice(list(self.status_mapping.keys()))
                prompt = template.format(status=status)
                payload = self._create_status_payload([self.status_mapping[status]])
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps(payload),
                "field_type": "status",
                "example_type": example_type
            })
        
        return examples

    def _generate_time_examples(self, count: int) -> List[Dict]:
        """Generate time-based examples"""
        examples = []
        
        time_templates = [
            ("Show tickets created {timeframe}", "created"),
            ("Find requests from {timeframe}", "from"),
            ("Get tickets {timeframe}", "simple"),
            ("Display items created in {timeframe}", "created_in"),
        ]
        
        timeframes = [
            ("today", "within_last", 1, "days"),
            ("yesterday", "within_last", 1, "days"),
            ("last week", "within_last", 7, "days"),
            ("last month", "within_last", 30, "days"),
            ("last 3 days", "within_last", 3, "days"),
            ("past 2 weeks", "within_last", 14, "days"),
        ]
        
        for i in range(count):
            template, time_type = random.choice(time_templates)
            timeframe, operator, value, unit = random.choice(timeframes)
            
            prompt = template.format(timeframe=timeframe)
            payload = self._create_time_payload(operator, value, unit)
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps(payload),
                "field_type": "time",
                "example_type": time_type
            })
        
        return examples

    def _generate_text_examples(self, count: int) -> List[Dict]:
        """Generate text search examples"""
        examples = []
        
        text_templates = [
            ("Show tickets with subject containing {keyword}", "contains"),
            ("Find tickets about {keyword}", "about"),
            ("Get requests with {keyword} in title", "in_title"),
            ("Display tickets mentioning {keyword}", "mentioning"),
        ]
        
        keywords = ["login", "error", "server", "network", "password", "access", "email", "printer"]
        
        for i in range(count):
            template, search_type = random.choice(text_templates)
            keyword = random.choice(keywords)
            
            prompt = template.format(keyword=keyword)
            payload = self._create_text_payload(keyword)
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps(payload),
                "field_type": "text",
                "example_type": search_type
            })
        
        return examples

    def _generate_combination_examples(self, count: int) -> List[Dict]:
        """Generate multi-field combination examples"""
        examples = []
        
        combination_templates = [
            ("Show {priority} priority {status} tickets", ["priority", "status"]),
            ("Find {status} tickets created {timeframe}", ["status", "time"]),
            ("Get {priority} priority tickets from {timeframe}", ["priority", "time"]),
            ("Display {status} {priority} priority items", ["status", "priority"]),
        ]
        
        for i in range(count):
            template, fields = random.choice(combination_templates)
            quals = []
            
            # Build prompt and payload based on fields
            format_args = {}
            
            if "priority" in fields:
                priority = random.choice(list(self.priority_mapping.keys()))
                format_args["priority"] = priority
                quals.append(self._create_priority_qual([self.priority_mapping[priority]]))
            
            if "status" in fields:
                status = random.choice(list(self.status_mapping.keys()))
                format_args["status"] = status
                quals.append(self._create_status_qual([self.status_mapping[status]]))
            
            if "time" in fields:
                timeframe = random.choice(["today", "last week", "yesterday"])
                format_args["timeframe"] = timeframe
                value = 1 if timeframe in ["today", "yesterday"] else 7
                quals.append(self._create_time_qual("within_last", value, "days"))
            
            prompt = template.format(**format_args)
            payload = {"qualDetails": {"quals": quals, "type": "FlatQualificationRest"}}
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps(payload),
                "field_type": "combination",
                "example_type": "_".join(fields)
            })
        
        return examples

    def _generate_natural_language_examples(self, count: int) -> List[Dict]:
        """Generate natural language variations"""
        examples = []
        
        natural_templates = [
            "What tickets need my attention?",
            "Show me urgent stuff",
            "Find things that are broken",
            "What's pending approval?",
            "Give me today's tickets",
            "Show critical issues",
            "Find tickets that are stuck",
            "What needs to be resolved?",
        ]
        
        # Map natural language to structured filters
        natural_mappings = {
            "What tickets need my attention?": self._create_status_payload([9, 10, 11]),  # open, in progress, pending
            "Show me urgent stuff": self._create_priority_payload([3, 4]),  # high, critical
            "Find things that are broken": self._create_status_payload([9]),  # open
            "What's pending approval?": self._create_status_payload([11]),  # pending
            "Give me today's tickets": self._create_time_payload("within_last", 1, "days"),
            "Show critical issues": self._create_priority_payload([4]),  # critical
            "Find tickets that are stuck": self._create_status_payload([98]),  # on hold
            "What needs to be resolved?": self._create_status_payload([9, 10]),  # open, in progress
        }
        
        for i in range(count):
            prompt = random.choice(natural_templates)
            payload = natural_mappings.get(prompt, {"qualDetails": {"quals": []}})
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps(payload),
                "field_type": "natural_language",
                "example_type": "conversational"
            })
        
        return examples

    def _generate_edge_cases(self, count: int) -> List[Dict]:
        """Generate edge cases and special scenarios"""
        examples = []
        
        edge_templates = [
            ("Show tickets with no assignee", "unassigned"),
            ("Find tickets with blank subject", "blank_subject"),
            ("Get tickets not assigned to anyone", "not_assigned"),
            ("Display tickets without priority", "no_priority"),
        ]
        
        edge_mappings = {
            "unassigned": self._create_assignee_blank_payload(),
            "blank_subject": self._create_subject_blank_payload(),
            "not_assigned": self._create_assignee_blank_payload(),
            "no_priority": self._create_priority_blank_payload(),
        }
        
        for i in range(count):
            template, edge_type = random.choice(edge_templates)
            prompt = template
            payload = edge_mappings[edge_type]
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps(payload),
                "field_type": "edge_case",
                "example_type": edge_type
            })
        
        return examples

    def _generate_complex_scenarios(self, count: int) -> List[Dict]:
        """Generate complex multi-condition scenarios"""
        examples = []
        
        # Complex scenarios with 3+ conditions
        for i in range(count):
            quals = []
            
            # Always include priority
            priority = random.choice(list(self.priority_mapping.keys()))
            quals.append(self._create_priority_qual([self.priority_mapping[priority]]))
            
            # Always include status
            status = random.choice(list(self.status_mapping.keys()))
            quals.append(self._create_status_qual([self.status_mapping[status]]))
            
            # Add time condition
            timeframe = random.choice([1, 7, 30])
            quals.append(self._create_time_qual("within_last", timeframe, "days"))
            
            # Create natural prompt
            time_text = "today" if timeframe == 1 else f"last {timeframe} days"
            prompt = f"Show {priority} priority {status} tickets from {time_text}"
            
            payload = {"qualDetails": {"quals": quals, "type": "FlatQualificationRest"}}
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps(payload),
                "field_type": "complex",
                "example_type": "three_conditions"
            })
        
        return examples

    # Helper methods for creating payload components
    def _create_priority_payload(self, values: List[int], operator: str = "in", excluded: List[int] = None) -> Dict:
        if operator == "not_in":
            values = excluded
        
        return {
            "qualDetails": {
                "quals": [self._create_priority_qual(values, operator)],
                "type": "FlatQualificationRest"
            }
        }

    def _create_status_payload(self, values: List[int], operator: str = "in", excluded: List[int] = None) -> Dict:
        if operator == "not_in":
            values = excluded
        
        return {
            "qualDetails": {
                "quals": [self._create_status_qual(values, operator)],
                "type": "FlatQualificationRest"
            }
        }

    def _create_time_payload(self, operator: str, value: int, unit: str) -> Dict:
        return {
            "qualDetails": {
                "quals": [self._create_time_qual(operator, value, unit)],
                "type": "FlatQualificationRest"
            }
        }

    def _create_text_payload(self, keyword: str) -> Dict:
        return {
            "qualDetails": {
                "quals": [{
                    "leftOperand": {"key": "request.subject", "type": "PropertyOperandRest"},
                    "operator": "contains",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "StringValueRest", "value": keyword}
                    }
                }],
                "type": "FlatQualificationRest"
            }
        }

    def _create_priority_qual(self, values: List[int], operator: str = "in") -> Dict:
        return {
            "leftOperand": {"key": "request.priorityId", "type": "PropertyOperandRest"},
            "operator": operator,
            "rightOperand": {
                "type": "ValueOperandRest",
                "value": {"type": "ListLongValueRest", "value": values}
            }
        }

    def _create_status_qual(self, values: List[int], operator: str = "in") -> Dict:
        return {
            "leftOperand": {"key": "request.statusId", "type": "PropertyOperandRest"},
            "operator": operator,
            "rightOperand": {
                "type": "ValueOperandRest",
                "value": {"type": "ListLongValueRest", "value": values}
            }
        }

    def _create_time_qual(self, operator: str, value: int, unit: str) -> Dict:
        return {
            "leftOperand": {"key": "created_date", "type": "VariableOperandRest"},
            "operator": operator,
            "rightOperand": {
                "type": "ValueOperandRest",
                "value": {"type": "DurationValueRest", "value": value, "unit": unit}
            }
        }

    def _create_assignee_blank_payload(self) -> Dict:
        return {
            "qualDetails": {
                "quals": [{
                    "leftOperand": {"key": "request.technicianId", "type": "PropertyOperandRest"},
                    "operator": "is_blank",
                    "rightOperand": None
                }],
                "type": "FlatQualificationRest"
            }
        }

    def _create_subject_blank_payload(self) -> Dict:
        return {
            "qualDetails": {
                "quals": [{
                    "leftOperand": {"key": "request.subject", "type": "PropertyOperandRest"},
                    "operator": "is_blank",
                    "rightOperand": None
                }],
                "type": "FlatQualificationRest"
            }
        }

    def _create_priority_blank_payload(self) -> Dict:
        return {
            "qualDetails": {
                "quals": [{
                    "leftOperand": {"key": "request.priorityId", "type": "PropertyOperandRest"},
                    "operator": "is_blank",
                    "rightOperand": None
                }],
                "type": "FlatQualificationRest"
            }
        }

if __name__ == "__main__":
    generator = TrainingDataGenerator()
    dataset = generator.generate_comprehensive_dataset(2000)
    
    # Save to file
    with open("comprehensive_training_data.json", "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✅ Generated {len(dataset['examples'])} training examples")
    print(f"📊 Categories: {dataset['metadata']['categories']}")
    print("💾 Saved to comprehensive_training_data.json")
