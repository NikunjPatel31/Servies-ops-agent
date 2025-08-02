#!/usr/bin/env python3
"""
Llama 3.2 LLM Agent for Filter Generation
=========================================

This module provides integration with Llama 3.2 model for intelligent
natural language to filter conversion. Supports multiple deployment options:
1. Ollama (local deployment)
2. Hugging Face Inference API
3. Custom API endpoints
"""

import json
import requests
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class Llama32Agent:
    """
    Llama 3.2 agent for intelligent filter generation
    """
    
    def __init__(self, 
                 deployment_type: str = "ollama",
                 api_endpoint: str = None,
                 api_key: str = None,
                 model_name: str = "llama3.2"):
        """
        Initialize Llama 3.2 agent
        
        Args:
            deployment_type: "ollama", "huggingface", or "custom"
            api_endpoint: Custom API endpoint URL
            api_key: API key for authentication (if required)
            model_name: Model name/identifier
        """
        self.deployment_type = deployment_type
        self.model_name = model_name
        self.api_key = api_key
        
        # Configure endpoint based on deployment type
        if deployment_type == "ollama":
            self.api_endpoint = api_endpoint or "http://localhost:11434/api/generate"
            # Fix chat endpoint configuration
            if api_endpoint and "/api/chat" in api_endpoint:
                self.chat_endpoint = api_endpoint
                self.api_endpoint = api_endpoint.replace("/api/chat", "/api/generate")
            else:
                self.chat_endpoint = "http://localhost:11434/api/chat"
            print(f"🔧 Configured Ollama endpoints:")
            print(f"   Generate: {self.api_endpoint}")
            print(f"   Chat: {self.chat_endpoint}")
        elif deployment_type == "huggingface":
            self.api_endpoint = f"https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-{model_name}"
            self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        elif deployment_type == "custom":
            self.api_endpoint = api_endpoint
        else:
            raise ValueError(f"Unsupported deployment type: {deployment_type}")
        
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
        
        print(f"🦙 Llama 3.2 Agent initialized with {deployment_type} deployment")

    def update_field_mappings(self, mappings: Dict[str, Dict[str, int]]):
        """Update field mappings from live API data"""
        self.field_mappings.update(mappings)
        print(f"🔄 Updated field mappings: {list(mappings.keys())}")

    def generate_filter_payload(self, user_prompt: str) -> Dict[str, Any]:
        """Generate filter payload using ONLY Llama 3.2 - Optimized for speed"""
        try:
            print(f"🦙 Using ONLY Llama 3.2 for: '{user_prompt}'")

            # Create intelligent response (rule-based for reliability)
            json_response = self._create_intelligent_llm_prompt(user_prompt)

            # Parse and validate response
            payload = self._parse_llm_response(json_response)

            print(f"🦙 Llama 3.2 generated payload for: '{user_prompt}'")
            return payload

        except Exception as e:
            print(f"❌ Llama generation failed: {e}")
            # Return error indicator so enhanced agent can fall back
            raise Exception(f"Llama 3.2 failed: {e}")



    def _create_llama_training_prompt(self, user_prompt: str) -> str:
        """Create a comprehensive training prompt for Llama model"""

        training_prompt = f"""You are an ITSM API qualification generator. Convert user requests to exact JSON format.

FIELD MAPPINGS:
- Priority: low=1, medium=2, high=3, critical=4 (use request.priorityId)
- Status: open=9, in_progress=10, pending=11, resolved=12, closed=13 (use request.statusId)
- Urgency: low=1, medium=2, high=3, critical=4 (use request.urgencyId)

RULES:
1. For "all requests" with NO filters: {{"qualDetails":{{"type":"FlatQualificationRest","quals":[]}}}}
2. For SINGLE filter key with single/multiple values: Create ONE qualification object
3. For MULTIPLE filter keys: Create SEPARATE qualification objects for EACH filter key
4. Each filter uses "operator":"in" and "type":"ListLongValueRest"

SINGLE FILTER EXAMPLES:
- "Get all requests" → {{"qualDetails":{{"type":"FlatQualificationRest","quals":[]}}}}
- "Get requests with priority high" → {{"qualDetails":{{"type":"FlatQualificationRest","quals":[{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.priorityId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[3]}}}}}}]}}}}
- "Get requests with priority high and low" -> {{"qualDetails":{{"type":"FlatQualificationRest","quals":[{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.priorityId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[3,1]}}}}}}]}}}}
- "Get requests with status open and closed" → {{"qualDetails":{{"type":"FlatQualificationRest","quals":[{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.statusId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[9,13]}}}}}}]}}}}

MULTIPLE FILTER EXAMPLES:
- "Get requests where status is open and priority is high" → {{"qualDetails":{{"type":"FlatQualificationRest","quals":[{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.statusId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[9]}}}}}},{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.priorityId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[3]}}}}}}]}}}}
- "Get requests where priority is high and status is open" → {{"qualDetails":{{"type":"FlatQualificationRest","quals":[{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.statusId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[3]}}}}}},{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.priorityId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[9]}}}}}}]}}}}
- "Get requests where status is open, closed and in progress and priority is high" → {{"qualDetails":{{"type":"FlatQualificationRest","quals":[{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.statusId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[9,13,10]}}}}}},{{"type":"RelationalQualificationRest","leftOperand":{{"type":"PropertyOperandRest","key":"request.priorityId"}},"operator":"in","rightOperand":{{"type":"ValueOperandRest","value":{{"type":"ListLongValueRest","value":[3]}}}}}}]}}}}

USER REQUEST: "{user_prompt}"

Generate ONLY the JSON qualification (no explanation):"""

        return training_prompt

    def _create_intelligent_llm_prompt(self, user_prompt: str) -> str:
        """Use Llama model to generate qualification JSON"""

        try:
            # Create comprehensive training prompt for Llama
            llama_prompt = self._create_llama_training_prompt(user_prompt)

            print(f"🦙 Sending prompt to Llama model...")
            print(f"🔍 User request: '{user_prompt}'")

            # Call Llama model via Ollama
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model_name,
                    "prompt": llama_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent output
                        "top_p": 0.9,
                        "num_predict": 500   # Limit response length
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                llama_response = response.json()
                generated_text = llama_response.get('response', '').strip()

                print(f"🦙 Llama raw response: {generated_text[:200]}...")

                # Extract JSON from Llama response
                json_start = generated_text.find('{')
                json_end = generated_text.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = generated_text[json_start:json_end]

                    # Validate JSON
                    try:
                        json.loads(json_str)
                        print(f"✅ Llama generated valid JSON qualification")
                        return json_str
                    except json.JSONDecodeError as e:
                        json.loads(json.dumps(json_str))
                        print(f"❌ Llama generated invalid JSON: {e}")
                        print(f"❌ Raw response: {generated_text}")

                        return json_str
                        raise Exception(f"Llama JSON validation failed: {e}")
                else:
                    print(f"❌ No JSON found in Llama response")
                    print(f"❌ Raw response: {generated_text}")
                    raise Exception("No valid JSON found in Llama response")
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                raise Exception(f"Ollama API failed with status {response.status_code}")

        except Exception as e:
            print(f"❌ CRITICAL: Llama model failed: {e}")
            print(f"❌ User prompt: '{user_prompt}'")
            raise Exception(f"Llama-only mode failed: {e}")


    def _create_llm_prompt(self, user_prompt: str) -> str:
        """Create optimized prompt for Llama 3.2 - Fast live processing"""

        # Create a concise, fast prompt for live data processing
        prompt = f"""Convert to JSON filter:

Query: "{user_prompt}"

IDs: Status(Open=9,Progress=10,Closed=11) Priority(High=3,Med=2,Low=1) Urgency(High=3,Med=2,Low=1)

JSON:
{{
  "qualDetails": {{
    "type": "FlatQualificationRest",
    "quals": [
      {{
        "type": "RelationalQualificationRest",
        "leftOperand": {{"type": "PropertyOperandRest", "key": "request.statusId"}},
        "operator": "in",
        "rightOperand": {{"type": "ValueOperandRest", "value": {{"type": "ListLongValueRest", "value": [9]}}}}
      }}
    ]
  }}
}}

Return JSON only:"""

        return prompt

    def _get_available_fields_summary(self) -> str:
        """Get summary of available fields and their values"""
        summary = []
        
        for field_type, mappings in self.field_mappings.items():
            if mappings:
                field_key = self.field_keys.get(field_type, f"request.{field_type}Id")
                values = list(mappings.items())[:5]  # Show first 5 values
                summary.append(f"- {field_key}: {dict(values)}")
        
        return "\n".join(summary) if summary else "No field mappings available"

    def _call_llama_api(self, prompt: str) -> str:
        """Call Llama 3.2 API based on deployment type"""
        
        if self.deployment_type == "ollama":
            return self._call_ollama_api(prompt)
        elif self.deployment_type == "huggingface":
            return self._call_huggingface_api(prompt)
        elif self.deployment_type == "custom":
            return self._call_custom_api(prompt)
        else:
            raise Exception(f"Unsupported deployment type: {self.deployment_type}")

    def _call_ollama_api(self, prompt: str) -> str:
        """Call Ollama local API"""
        try:
            # Use generate endpoint directly (more stable)
            print(f"🦙 Trying Llama 3.2 agent...")
            return self._call_ollama_generate(prompt)

        except Exception as e:
            print(f"⚠️ Ollama chat API failed: {e}")
            raise e

    def _call_ollama_generate(self, prompt: str) -> str:
        """Call Ollama generate endpoint (fallback)"""
        headers = {"Content-Type": "application/json"}

        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,  # More deterministic
                "top_p": 0.1,        # More focused
                "num_predict": 1000,  # Enough for JSON response
                "stop": ["\n\n", "```", "Output:", "Result:", "Response:", "Here is"],  # Stop tokens
                "repeat_penalty": 1.1
            }
        }
        
        response = requests.post(self.api_endpoint, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result["response"]

    def _call_huggingface_api(self, prompt: str) -> str:
        """Call Hugging Face Inference API"""
        if not self.api_key:
            raise Exception("Hugging Face API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.1,
                "max_new_tokens": 2000,
                "return_full_text": False
            }
        }

        response = requests.post(self.api_endpoint, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        return str(result)

    def _call_custom_api(self, prompt: str) -> str:
        """Call custom API endpoint"""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Assume OpenAI-compatible format for custom endpoints
        data = {
            "model": self.model_name,
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

        response = requests.post(self.api_endpoint, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate Llama response"""
        try:
            # Debug: Print raw Llama response
            print(f"🔍 DEBUG: Raw Llama response (first 300 chars): {response[:300]}")
            print(f"🔍 DEBUG: Response length: {len(response)}")

            # Extract JSON from response
            response = response.strip()

            # Remove markdown code blocks if present
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            # Find JSON object in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            print(f"🔍 DEBUG: JSON start_idx: {start_idx}, end_idx: {end_idx}")

            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                print(f"🔍 DEBUG: Extracted JSON string: {json_str[:200]}...")
                payload = json.loads(json_str)

                # Validate structure
                if 'qualDetails' in payload and 'quals' in payload['qualDetails']:
                    print("✅ DEBUG: Valid payload structure found")
                    return payload
                else:
                    print("⚠️ Invalid payload structure from Llama")
                    print(f"🔍 DEBUG: Payload keys: {list(payload.keys()) if isinstance(payload, dict) else 'Not a dict'}")
                    return {"qualDetails": {"quals": [], "type": "FlatQualificationRest"}}
            else:
                print("⚠️ No valid JSON found in Llama response")
                print(f"🔍 DEBUG: Response after cleanup: {response[:200]}...")
                return {"qualDetails": {"quals": [], "type": "FlatQualificationRest"}}

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"🔍 DEBUG: Failed to parse: {response[start_idx:end_idx] if 'start_idx' in locals() and 'end_idx' in locals() else 'N/A'}")
            return {"qualDetails": {"quals": [], "type": "FlatQualificationRest"}}
        except Exception as e:
            print(f"⚠️ Response parsing error: {e}")
            return {"qualDetails": {"quals": [], "type": "FlatQualificationRest"}}

    def test_connection(self) -> bool:
        """Test connection to Llama 3.2 deployment"""
        try:
            test_prompt = "Convert this to JSON: Get requests with high priority"
            response = self._call_llama_api(test_prompt)
            print(f"✅ Llama 3.2 connection test successful")
            print(f"📝 Test response: {response[:100]}...")
            return True
        except Exception as e:
            print(f"❌ Llama 3.2 connection test failed: {e}")
            return False
