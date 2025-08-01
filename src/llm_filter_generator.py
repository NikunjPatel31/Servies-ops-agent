#!/usr/bin/env python3
"""
LLM-Based Dynamic Filter Generator
Uses trained language model to convert natural language to filter payloads
"""

import json
import re
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class LLMFilterGenerator:
    def __init__(self, model_endpoint: str = None):
        self.model_endpoint = model_endpoint
        
        # Dynamic mappings (fetched from APIs)
        self.priority_mapping = {}
        self.status_mapping = {}
        self.urgency_mapping = {}
        self.user_mapping = {}
        self.location_mapping = {}
        self.category_mapping = {}
        
        # Load training examples for few-shot learning
        self.training_examples = self._load_training_examples()
        
    def _load_training_examples(self) -> List[Dict]:
        """Load curated training examples for few-shot prompting"""
        return [
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
                        ]
                    }
                }
            },
            {
                "prompt": "Find tickets created in the last 7 days",
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
                        ]
                    }
                }
            },
            {
                "prompt": "Show tickets not assigned to anyone",
                "payload": {
                    "qualDetails": {
                        "quals": [
                            {
                                "leftOperand": {"key": "request.technicianId", "type": "PropertyOperandRest"},
                                "operator": "is_blank",
                                "rightOperand": None
                            }
                        ]
                    }
                }
            }
        ]

    def update_mappings(self, mappings: Dict[str, Dict[str, int]]):
        """Update field mappings from API responses"""
        self.priority_mapping = mappings.get('priority', {})
        self.status_mapping = mappings.get('status', {})
        self.urgency_mapping = mappings.get('urgency', {})
        self.user_mapping = mappings.get('users', {})
        self.location_mapping = mappings.get('locations', {})
        self.category_mapping = mappings.get('categories', {})

    def generate_filter_payload(self, user_prompt: str) -> Dict[str, Any]:
        """Generate filter payload from natural language prompt"""
        
        # Try LLM-based generation first
        if self.model_endpoint:
            try:
                return self._llm_generate_payload(user_prompt)
            except Exception as e:
                print(f"LLM generation failed: {e}")
                # Fall back to rule-based
        
        # Fallback to enhanced rule-based generation
        return self._rule_based_generate_payload(user_prompt)

    def _llm_generate_payload(self, user_prompt: str) -> Dict[str, Any]:
        """Use LLM to generate filter payload"""
        
        # Create few-shot prompt
        system_prompt = self._create_system_prompt()
        few_shot_examples = self._create_few_shot_examples()
        
        full_prompt = f"""
{system_prompt}

{few_shot_examples}

Now generate the filter payload for this prompt:
User: "{user_prompt}"
Assistant: """

        # Call LLM API (OpenAI, Anthropic, or local model)
        response = self._call_llm_api(full_prompt)
        
        # Parse and validate response
        return self._parse_llm_response(response)

    def _create_system_prompt(self) -> str:
        """Create system prompt with current mappings"""
        return f"""
You are an expert at converting natural language queries into structured filter payloads for a ticketing system.

Current System Mappings:
- Priority: {self.priority_mapping}
- Status: {self.status_mapping}
- Urgency: {self.urgency_mapping}
- Users: {dict(list(self.user_mapping.items())[:5])}...
- Locations: {dict(list(self.location_mapping.items())[:5])}...
- Categories: {dict(list(self.category_mapping.items())[:5])}...

Rules:
1. Always use exact field keys: request.priorityId, request.statusId, etc.
2. Use numeric IDs from mappings, not text labels
3. For time filters, use VariableOperandRest type
4. For property filters, use PropertyOperandRest type
5. Return valid JSON only

Field Mapping:
- Priority → request.priorityId
- Status → request.statusId  
- Urgency → request.urgencyId
- Assignee → request.technicianId
- Location → request.locationId
- Category → request.categoryId
- Created Date → created_date
- Resolved Date → resolved_date
"""

    def _create_few_shot_examples(self) -> str:
        """Create few-shot examples string"""
        examples_str = ""
        for i, example in enumerate(self.training_examples[:3]):
            examples_str += f"""
Example {i+1}:
User: "{example['prompt']}"
Assistant: {json.dumps(example['payload'], indent=2)}
"""
        return examples_str

    def _call_llm_api(self, prompt: str) -> str:
        """Call LLM API (implement based on your chosen provider)"""
        if not self.model_endpoint:
            raise Exception("No LLM endpoint configured")
        
        # Example for OpenAI API
        headers = {
            "Authorization": f"Bearer {self._get_api_key()}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1000
        }
        
        response = requests.post(self.model_endpoint, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]

    def _get_api_key(self) -> str:
        """Get API key from environment or config"""
        import os
        return os.getenv("OPENAI_API_KEY", "")

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                payload = json.loads(json_match.group())
                return self._validate_payload(payload)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")
            raise

    def _validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated payload structure"""
        required_structure = {
            "qualDetails": {
                "quals": []
            }
        }
        
        if "qualDetails" not in payload:
            raise ValueError("Missing qualDetails in payload")
        
        if "quals" not in payload["qualDetails"]:
            raise ValueError("Missing quals in qualDetails")
        
        # Validate each qual
        for qual in payload["qualDetails"]["quals"]:
            self._validate_qual(qual)
        
        return payload

    def _validate_qual(self, qual: Dict[str, Any]):
        """Validate individual qualification"""
        required_fields = ["leftOperand", "operator"]
        
        for field in required_fields:
            if field not in qual:
                raise ValueError(f"Missing {field} in qualification")
        
        # Validate leftOperand
        if "key" not in qual["leftOperand"]:
            raise ValueError("Missing key in leftOperand")
        
        # Validate operator
        valid_operators = ["in", "not_in", "contains", "within_last", "before", "after", "is_blank"]
        if qual["operator"] not in valid_operators:
            raise ValueError(f"Invalid operator: {qual['operator']}")

    def _rule_based_generate_payload(self, user_prompt: str) -> Dict[str, Any]:
        """Enhanced rule-based fallback generation"""
        prompt_lower = user_prompt.lower()
        quals = []
        
        # Priority detection
        priority_quals = self._detect_priority_filters(prompt_lower)
        quals.extend(priority_quals)
        
        # Status detection  
        status_quals = self._detect_status_filters(prompt_lower)
        quals.extend(status_quals)
        
        # Time detection
        time_quals = self._detect_time_filters(prompt_lower)
        quals.extend(time_quals)
        
        # User detection
        user_quals = self._detect_user_filters(prompt_lower)
        quals.extend(user_quals)
        
        return {
            "qualDetails": {
                "quals": quals,
                "type": "FlatQualificationRest"
            }
        }

    def _detect_priority_filters(self, prompt: str) -> List[Dict]:
        """Detect priority-related filters"""
        quals = []
        
        # Priority keywords mapping
        priority_patterns = {
            r'\b(high|urgent|p1|critical)\b': [3, 4],
            r'\b(medium|normal|p2)\b': [2],
            r'\b(low|p3|p4)\b': [1],
            r'\b(critical|p1)\b': [4]
        }
        
        for pattern, values in priority_patterns.items():
            if re.search(pattern, prompt):
                quals.append({
                    "leftOperand": {"key": "request.priorityId", "type": "PropertyOperandRest"},
                    "operator": "in",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "ListLongValueRest", "value": values}
                    }
                })
                break
        
        return quals

    def _detect_status_filters(self, prompt: str) -> List[Dict]:
        """Detect status-related filters"""
        quals = []
        
        status_patterns = {
            r'\b(open|new)\b': [9],
            r'\b(in.progress|working|active)\b': [10],
            r'\b(pending|waiting)\b': [11],
            r'\b(resolved|fixed)\b': [12],
            r'\b(closed|done|completed)\b': [13]
        }
        
        for pattern, values in status_patterns.items():
            if re.search(pattern, prompt):
                quals.append({
                    "leftOperand": {"key": "request.statusId", "type": "PropertyOperandRest"},
                    "operator": "in",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "ListLongValueRest", "value": values}
                    }
                })
                break
        
        return quals

    def _detect_time_filters(self, prompt: str) -> List[Dict]:
        """Detect time-related filters"""
        quals = []
        
        time_patterns = [
            (r'\b(today|last 24 hours)\b', 1, "days"),
            (r'\b(yesterday)\b', 1, "days"),
            (r'\b(last week|past week)\b', 7, "days"),
            (r'\b(last month|past month)\b', 30, "days"),
            (r'\blast (\d+) days?\b', None, "days"),
        ]
        
        for pattern, value, unit in time_patterns:
            match = re.search(pattern, prompt)
            if match:
                if value is None:
                    value = int(match.group(1))
                
                quals.append({
                    "leftOperand": {"key": "created_date", "type": "VariableOperandRest"},
                    "operator": "within_last",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "DurationValueRest", "value": value, "unit": unit}
                    }
                })
                break
        
        return quals

    def _detect_user_filters(self, prompt: str) -> List[Dict]:
        """Detect user/assignee filters"""
        quals = []
        
        # Check for user names in prompt
        for user_name, user_id in self.user_mapping.items():
            if user_name.lower() in prompt:
                quals.append({
                    "leftOperand": {"key": "request.technicianId", "type": "PropertyOperandRest"},
                    "operator": "in",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "ListLongValueRest", "value": [user_id]}
                    }
                })
                break
        
        # Check for unassigned
        if re.search(r'\b(unassigned|no.assignee|not.assigned)\b', prompt):
            quals.append({
                "leftOperand": {"key": "request.technicianId", "type": "PropertyOperandRest"},
                "operator": "is_blank",
                "rightOperand": None
            })
        
        return quals

# Example usage
if __name__ == "__main__":
    generator = LLMFilterGenerator()
    
    # Update with current system mappings
    mappings = {
        'priority': {'low': 1, 'medium': 2, 'high': 3, 'critical': 4},
        'status': {'open': 9, 'in progress': 10, 'pending': 11, 'closed': 13},
        'users': {'john': 45, 'jane': 78}
    }
    generator.update_mappings(mappings)
    
    # Test prompts
    test_prompts = [
        "Show high priority open tickets",
        "Find tickets created last week",
        "Get unassigned critical issues",
        "Display tickets assigned to John"
    ]
    
    for prompt in test_prompts:
        try:
            payload = generator.generate_filter_payload(prompt)
            print(f"Prompt: {prompt}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print("-" * 50)
        except Exception as e:
            print(f"Error processing '{prompt}': {e}")
