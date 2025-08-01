#!/usr/bin/env python3
"""
Dynamic LLM-Powered Filter Agent
Replaces regex-based approach with intelligent LLM understanding
"""

import json
import requests
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class DynamicLLMAgent:
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"
        
        # Dynamic mappings (fetched from APIs)
        self.field_mappings = {
            'priority': {},
            'status': {},
            'urgency': {},
            'users': {},
            'locations': {},
            'categories': {}
        }
        
        # Field key mappings
        self.field_keys = {
            'priority': 'request.priorityId',
            'status': 'request.statusId',
            'urgency': 'request.urgencyId',
            'assignee': 'request.technicianId',
            'technician': 'request.technicianId',
            'location': 'request.locationId',
            'category': 'request.categoryId',
            'requester': 'request.requesterId',
            'subject': 'request.subject',
            'description': 'request.description',
            'created_date': 'created_date',
            'resolved_date': 'resolved_date',
            'closed_date': 'ticket_closed_date',
            'due_date': 'request.dueDate'
        }

    def update_field_mappings(self, mappings: Dict[str, Dict[str, int]]):
        """Update field mappings from live API data"""
        self.field_mappings.update(mappings)
        print(f"🔄 Updated field mappings: {list(mappings.keys())}")

    def generate_filter_payload(self, user_prompt: str) -> Dict[str, Any]:
        """Generate filter payload using LLM intelligence"""
        try:
            # Create intelligent prompt for LLM
            llm_prompt = self._create_llm_prompt(user_prompt)
            
            # Get LLM response
            llm_response = self._call_openai_api(llm_prompt)
            
            # Parse and validate response
            payload = self._parse_llm_response(llm_response)
            
            print(f"🤖 LLM generated payload for: '{user_prompt}'")
            return payload
            
        except Exception as e:
            print(f"❌ LLM generation failed: {e}")
            # Fallback to basic structure
            return {"qualDetails": {"quals": [], "type": "FlatQualificationRest"}}

    def _create_llm_prompt(self, user_prompt: str) -> str:
        """Create comprehensive prompt for LLM"""
        
        system_context = f"""
You are an expert at converting natural language queries into structured filter payloads for a ticketing system.

CURRENT SYSTEM MAPPINGS:
Priority: {self.field_mappings.get('priority', {})}
Status: {self.field_mappings.get('status', {})}
Urgency: {self.field_mappings.get('urgency', {})}
Users: {dict(list(self.field_mappings.get('users', {}).items())[:10])}
Locations: {dict(list(self.field_mappings.get('locations', {}).items())[:10])}
Categories: {dict(list(self.field_mappings.get('categories', {}).items())[:10])}

FIELD MAPPING RULES:
- Priority → request.priorityId (use numeric IDs from mapping)
- Status → request.statusId (use numeric IDs from mapping)
- Urgency → request.urgencyId (use numeric IDs from mapping)
- Assignee/Technician → request.technicianId (use numeric IDs from mapping)
- Location → request.locationId (use numeric IDs from mapping)
- Category → request.categoryId (use numeric IDs from mapping)
- Requester → request.requesterId (use numeric IDs from mapping)
- Subject → request.subject (string operations)
- Created Date → created_date (date operations)
- Resolved Date → resolved_date (date operations)
- Closed Date → ticket_closed_date (date operations)

OPERAND TYPES:
- Property fields (request.*): "type": "PropertyOperandRest"
- System fields (*_date): "type": "VariableOperandRest"

VALUE TYPES:
- Numeric lists: "type": "ListLongValueRest", "value": [1,2,3]
- String values: "type": "StringValueRest", "value": "text"
- Date values: "type": "DateValueRest", "value": "2024-01-01T00:00:00Z"
- Duration values: "type": "DurationValueRest", "value": 7, "unit": "days"
- Date ranges: "type": "BetweenDateValueRest", "from": "...", "to": "..."

OPERATORS:
- in, not_in (for lists)
- contains, equal_case_insensitive, start_with (for strings)
- before, after, between, within_last (for dates)
- is_blank, is_not_blank (for null checks)

EXAMPLES:
"""

        examples = [
            {
                "prompt": "Show high priority open tickets",
                "payload": {
                    "qualDetails": {
                        "quals": [
                            {
                                "leftOperand": {"key": "request.priorityId", "type": "PropertyOperandRest"},
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {"type": "ListLongValueRest", "value": [3]}
                                }
                            },
                            {
                                "leftOperand": {"key": "request.statusId", "type": "PropertyOperandRest"},
                                "operator": "in",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {"type": "ListLongValueRest", "value": [9]}
                                }
                            }
                        ],
                        "type": "FlatQualificationRest"
                    }
                }
            },
            {
                "prompt": "Find tickets created in last 7 days",
                "payload": {
                    "qualDetails": {
                        "quals": [
                            {
                                "leftOperand": {"key": "created_date", "type": "VariableOperandRest"},
                                "operator": "within_last",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {"type": "DurationValueRest", "value": 7, "unit": "days"}
                                }
                            }
                        ],
                        "type": "FlatQualificationRest"
                    }
                }
            },
            {
                "prompt": "Show tickets with subject containing error",
                "payload": {
                    "qualDetails": {
                        "quals": [
                            {
                                "leftOperand": {"key": "request.subject", "type": "PropertyOperandRest"},
                                "operator": "contains",
                                "rightOperand": {
                                    "type": "ValueOperandRest",
                                    "value": {"type": "StringValueRest", "value": "error"}
                                }
                            }
                        ],
                        "type": "FlatQualificationRest"
                    }
                }
            }
        ]

        examples_text = ""
        for i, example in enumerate(examples, 1):
            examples_text += f"""
Example {i}:
User: "{example['prompt']}"
Response: {json.dumps(example['payload'], indent=2)}
"""

        full_prompt = f"""
{system_context}
{examples_text}

IMPORTANT RULES:
1. ALWAYS use exact numeric IDs from the mappings above
2. NEVER use text labels in filters (e.g., use 3 not "high")
3. Use appropriate operand types (PropertyOperandRest vs VariableOperandRest)
4. Include "type": "FlatQualificationRest" in qualDetails
5. Return ONLY valid JSON, no explanations
6. Handle synonyms (urgent=high, P1=critical, etc.)
7. Support multiple values (high and medium = [3,2])
8. Handle negations (not closed = not_in [13])

Now convert this user query to a filter payload:
User: "{user_prompt}"
Response:"""

        return full_prompt

    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with the prompt"""
        if not self.openai_api_key:
            raise Exception("OpenAI API key not configured")

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at converting natural language to structured filter payloads. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }

        response = requests.post(self.openai_endpoint, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            # Extract JSON from response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            # Parse JSON
            payload = json.loads(response.strip())
            
            # Validate structure
            self._validate_payload(payload)
            
            return payload
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response: {response}")
            raise Exception(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            print(f"❌ Payload validation error: {e}")
            raise

    def _validate_payload(self, payload: Dict[str, Any]):
        """Validate payload structure"""
        if "qualDetails" not in payload:
            raise ValueError("Missing 'qualDetails' in payload")
        
        qual_details = payload["qualDetails"]
        if "quals" not in qual_details:
            raise ValueError("Missing 'quals' in qualDetails")
        
        # Validate each qualification
        for i, qual in enumerate(qual_details["quals"]):
            try:
                self._validate_qualification(qual)
            except Exception as e:
                raise ValueError(f"Invalid qualification at index {i}: {e}")

    def _validate_qualification(self, qual: Dict[str, Any]):
        """Validate individual qualification"""
        required_fields = ["leftOperand", "operator"]
        
        for field in required_fields:
            if field not in qual:
                raise ValueError(f"Missing '{field}' in qualification")
        
        # Validate leftOperand
        left_operand = qual["leftOperand"]
        if "key" not in left_operand or "type" not in left_operand:
            raise ValueError("leftOperand must have 'key' and 'type'")
        
        # Validate operator
        valid_operators = [
            "in", "not_in", "contains", "equal_case_insensitive", 
            "start_with", "before", "after", "between", "within_last",
            "is_blank", "is_not_blank"
        ]
        
        if qual["operator"] not in valid_operators:
            raise ValueError(f"Invalid operator: {qual['operator']}")
        
        # Validate rightOperand (if present)
        if "rightOperand" in qual and qual["rightOperand"] is not None:
            right_operand = qual["rightOperand"]
            if "type" not in right_operand or "value" not in right_operand:
                raise ValueError("rightOperand must have 'type' and 'value'")

    def generate_training_examples(self, count: int = 100) -> List[Dict]:
        """Generate training examples for fine-tuning"""
        examples = []
        
        # Priority examples
        priority_examples = [
            ("Show high priority tickets", [3]),
            ("Find critical and urgent issues", [4]),
            ("Get P1 and P2 tickets", [4, 3]),
            ("Display medium or low priority items", [2, 1]),
            ("Show non-critical tickets", "not_in", [4]),
        ]
        
        for prompt, values in priority_examples:
            operator = "not_in" if isinstance(values, tuple) else "in"
            if operator == "not_in":
                values = values[1] if isinstance(values, tuple) else values
            
            examples.append({
                "prompt": prompt,
                "completion": json.dumps({
                    "qualDetails": {
                        "quals": [{
                            "leftOperand": {"key": "request.priorityId", "type": "PropertyOperandRest"},
                            "operator": operator,
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {"type": "ListLongValueRest", "value": values}
                            }
                        }],
                        "type": "FlatQualificationRest"
                    }
                })
            })
        
        # Add more examples for other fields...
        # (Status, time, combinations, etc.)
        
        return examples[:count]

# Example usage and testing
if __name__ == "__main__":
    # Initialize agent
    agent = DynamicLLMAgent()
    
    # Update with sample mappings
    sample_mappings = {
        'priority': {'low': 1, 'medium': 2, 'high': 3, 'critical': 4},
        'status': {'open': 9, 'in progress': 10, 'pending': 11, 'resolved': 12, 'closed': 13},
        'users': {'john': 45, 'jane': 78, 'bob': 23},
        'locations': {'new york': 10, 'london': 15, 'tokyo': 20}
    }
    agent.update_field_mappings(sample_mappings)
    
    # Test prompts
    test_prompts = [
        "Show high priority open tickets",
        "Find tickets created last week",
        "Get critical issues assigned to John",
        "Display tickets from New York with medium priority",
        "Show tickets not closed",
        "Find tickets with subject containing login"
    ]
    
    print("🧪 Testing Dynamic LLM Agent:")
    print("=" * 50)
    
    for prompt in test_prompts:
        try:
            payload = agent.generate_filter_payload(prompt)
            print(f"✅ Prompt: {prompt}")
            print(f"📋 Payload: {json.dumps(payload, indent=2)}")
            print("-" * 30)
        except Exception as e:
            print(f"❌ Error for '{prompt}': {e}")
            print("-" * 30)
