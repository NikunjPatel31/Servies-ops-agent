#!/usr/bin/env python3
"""
API Endpoint Server
===================

Flask server that takes user prompts and executes the appropriate API calls.
User sends: {"request": "Get all the request with priority as low"}
Server responds with actual API results.
"""

from flask import Flask, request, jsonify
from request_search_api_agent import RequestSearchAPIAgent
from multi_endpoint_agent import MultiEndpointAgent
import requests
import json
import re
from urllib.parse import urlencode
import sys
import os
from datetime import datetime

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
from api_config import APIConfig

app = Flask(__name__)

class APIExecutor:
    """Executes API calls based on user prompts"""

    def __init__(self):
        self.agent = RequestSearchAPIAgent("APIExecutor")
        self.multi_agent = MultiEndpointAgent()
        # Use configuration
        self.config = APIConfig

        # Token cache
        self.cached_token = None
        self.token_expiry = None

        # Status mapping cache
        self.status_mapping = {}
        self.status_mapping_loaded = False

        # Remove static parsing - rely on multi-endpoint agent only
        print("🎯 API Endpoint Server initialized - Using dynamic multi-endpoint agent for all filter generation")

    def get_access_token(self):
        """Get access token using OAuth endpoint"""
        try:
            # Check if we have a valid cached token
            if self.cached_token and self.token_expiry:
                import datetime
                if datetime.datetime.now() < self.token_expiry:
                    return self.cached_token

            print("🔑 Fetching new access token...")

            # Prepare OAuth request
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'en-GB,en;q=0.9',
                'Authorization': self.config.CLIENT_AUTH,
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self.config.BASE_URL,
                'Referer': f'{self.config.BASE_URL}/login?redirectFrom=%2Ft%2Frequest%2F',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }

            # Prepare form data
            data = {
                'username': self.config.USERNAME,
                'password': self.config.PASSWORD,
                'grant_type': 'password'
            }

            # Make OAuth request
            response = requests.post(
                self.config.OAUTH_URL,
                headers=headers,
                data=data,
                verify=False,  # --insecure equivalent
                timeout=self.config.REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)  # Default 1 hour

                if access_token:
                    # Cache the token
                    self.cached_token = access_token
                    import datetime
                    self.token_expiry = datetime.datetime.now() + datetime.timedelta(seconds=expires_in - self.config.TOKEN_REFRESH_BUFFER)

                    print(f"✅ Token obtained successfully (expires in {expires_in}s)")
                    return access_token
                else:
                    print("❌ No access token in response")
                    return None
            else:
                print(f"❌ OAuth failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ Token retrieval error: {str(e)}")
            return None

    def get_status_mapping(self):
        """Get status mapping from the API with fallback"""
        try:
            # Return cached mapping if available
            if self.status_mapping_loaded:
                return self.status_mapping

            print("📋 Fetching status mapping...")

            # Get access token
            auth_token = self.get_access_token()
            if not auth_token:
                print("❌ Cannot fetch status mapping - no auth token")
                return self._get_fallback_status_mapping()

            # Prepare headers
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'Authorization': f'Bearer {auth_token}',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Origin': self.config.BASE_URL,
                'Referer': f'{self.config.BASE_URL}/admin/status/?type=request',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
            }

            # Make status API request
            response = requests.post(
                self.config.STATUS_SEARCH_URL,
                headers=headers,
                json={},  # Empty body as per your example
                verify=False,
                timeout=self.config.REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                try:
                    response_data = response.json()

                    # Handle different response formats
                    if isinstance(response_data, list):
                        statuses = response_data
                    elif isinstance(response_data, dict):
                        # Check if it's a paginated response
                        if 'objectList' in response_data:
                            statuses = response_data['objectList']
                        elif 'content' in response_data:
                            statuses = response_data['content']
                        else:
                            # Assume the dict itself contains status data
                            statuses = [response_data]
                    else:
                        print(f"❌ Unexpected response format: {type(response_data)}")
                        return self._get_fallback_status_mapping()

                    # Build status mapping: name -> id
                    self.status_mapping = {}
                    for status in statuses:
                        if not isinstance(status, dict):
                            print(f"❌ Expected dict, got: {type(status)}")
                            continue

                        status_name = status.get('name', '').lower()
                        status_id = status.get('id')
                        system_name = status.get('systemName', '').lower()

                        if status_name and status_id:
                            self.status_mapping[status_name] = status_id
                            # Also map system name if different
                            if system_name and system_name != status_name:
                                self.status_mapping[system_name] = status_id

                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"   Response text: {response.text[:200]}...")
                    return self._get_fallback_status_mapping()

                self.status_mapping_loaded = True
                print(f"✅ Status mapping loaded: {len(self.status_mapping)} statuses")
                print(f"   Available statuses: {list(self.status_mapping.keys())}")

                return self.status_mapping
            else:
                print(f"❌ Status API failed: {response.status_code}")
                if response.status_code == 502:
                    print("   Server error - using fallback status mapping")
                return self._get_fallback_status_mapping()

        except Exception as e:
            print(f"❌ Status mapping error: {str(e)}")
            return self._get_fallback_status_mapping()

    def _get_fallback_status_mapping(self):
        """Fallback status mapping based on common statuses"""
        print("🔄 Using fallback status mapping")
        fallback_mapping = {
            "open": 9,
            "in progress": 10,
            "pending": 11,
            "resolved": 12,
            "closed": 13,
            "testing1": 14  # Based on your example
        }

        self.status_mapping = fallback_mapping
        self.status_mapping_loaded = True
        print(f"✅ Fallback status mapping loaded: {len(fallback_mapping)} statuses")
        print(f"   Available statuses: {list(fallback_mapping.keys())}")

        return fallback_mapping

    def get_user_mapping(self):
        """Get user mapping from the API"""
        try:
            # Return cached mapping if available
            if hasattr(self, 'user_mapping_loaded') and self.user_mapping_loaded:
                return getattr(self, 'user_mapping', {})

            print("👥 Fetching user mapping...")

            # Get access token
            auth_token = self.get_access_token()
            if not auth_token:
                print("❌ Cannot fetch user mapping - no auth token")
                return {}

            # Prepare headers
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'Authorization': f'Bearer {auth_token}',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Origin': self.config.BASE_URL,
                'Referer': f'{self.config.BASE_URL}/admin/users/',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
            }

            # Make user API request
            user_api_url = self.config.USER_SEARCH_URL

            response = requests.post(
                user_api_url,
                headers=headers,
                json={},  # Empty body or provide required parameters
                verify=False,
                timeout=self.config.REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                try:
                    response_data = response.json()

                    # Handle different response formats
                    if isinstance(response_data, list):
                        users = response_data
                    elif isinstance(response_data, dict):
                        # Check if it's a paginated response
                        if 'objectList' in response_data:
                            users = response_data['objectList']
                        elif 'content' in response_data:
                            users = response_data['content']
                        else:
                            users = [response_data]
                    else:
                        print(f"❌ Unexpected user response format: {type(response_data)}")
                        return {}

                    # Build user mapping: name -> id
                    self.user_mapping = {}
                    for user in users:
                        if not isinstance(user, dict):
                            continue

                        user_name = user.get('name', '').lower()
                        user_id = user.get('id')
                        login_name = user.get('loginName', '').lower()
                        email = user.get('email', '').lower()

                        if user_name and user_id:
                            self.user_mapping[user_name] = user_id
                            # Also map login name and email if different
                            if login_name and login_name != user_name:
                                self.user_mapping[login_name] = user_id
                            if email and email != user_name:
                                self.user_mapping[email] = user_id

                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    return {}

                self.user_mapping_loaded = True
                print(f"✅ User mapping loaded: {len(self.user_mapping)} users")
                print(f"   Available users: {list(self.user_mapping.keys())[:5]}...")  # Show first 5

                return self.user_mapping
            else:
                print(f"❌ User API failed: {response.status_code} - {response.text}")
                return {}

        except Exception as e:
            print(f"❌ User mapping error: {str(e)}")
            return {}
    
    def parse_user_prompt(self, user_prompt):
        """Parse user prompt and determine API parameters"""
        prompt_lower = user_prompt.lower()
        
        # Default parameters from config
        params = {
            "offset": self.config.DEFAULT_OFFSET,
            "size": self.config.DEFAULT_SIZE,
            "sort_by": self.config.DEFAULT_SORT_BY
        }
        
        # Parse pagination
        if "first" in prompt_lower or "page 1" in prompt_lower:
            params["offset"] = 0
        elif "next" in prompt_lower or "page 2" in prompt_lower:
            params["offset"] = 25
        elif "more" in prompt_lower:
            params["size"] = 50
        
        # Parse sorting
        if "sort by priority" in prompt_lower or "priority order" in prompt_lower:
            params["sort_by"] = "priority"
        elif "sort by date" in prompt_lower or "creation time" in prompt_lower:
            params["sort_by"] = "createdTime"
        
        return params
    
    # All static parsing methods removed - using dynamic multi-endpoint agent only

    def extract_request_id(self, user_prompt):
        """Extract specific request ID from user prompt"""
        prompt_lower = user_prompt.lower()

        # Look for patterns like:
        # "get request 2", "show me request INC-2", "details of request 2"
        # "fetch request with id 2", "request number 2"

        import re

        # Pattern 1: "request 2", "request id 2", "request number 2"
        pattern1 = r'request\s+(?:id\s+|number\s+)?(\d+)'
        match1 = re.search(pattern1, prompt_lower)
        if match1:
            return int(match1.group(1))

        # Pattern 2: "INC-2", "REQ-2", etc.
        pattern2 = r'(?:inc|req|ticket|request)[-\s]*(\d+)'
        match2 = re.search(pattern2, prompt_lower)
        if match2:
            return int(match2.group(1))

        # Pattern 3: "id 2", "ID: 2"
        pattern3 = r'id\s*:?\s*(\d+)'
        match3 = re.search(pattern3, prompt_lower)
        if match3:
            return int(match3.group(1))

        # Pattern 4: Just a number if context suggests it's a request
        if any(keyword in prompt_lower for keyword in ['get', 'show', 'fetch', 'details', 'info']):
            pattern4 = r'\b(\d+)\b'
            matches = re.findall(pattern4, prompt_lower)
            if len(matches) == 1:  # Only if there's exactly one number
                return int(matches[0])

        return None

    def is_specific_request_query(self, user_prompt):
        """Check if the query is asking for a specific request"""
        prompt_lower = user_prompt.lower()

        # Keywords that suggest specific request query
        specific_keywords = [
            'get request', 'show request', 'fetch request', 'request details',
            'details of request', 'info about request', 'request info',
            'inc-', 'req-', 'ticket', 'request id', 'request number'
        ]

        # Check if any specific keyword is present
        has_specific_keyword = any(keyword in prompt_lower for keyword in specific_keywords)

        # Check if there's a request ID
        request_id = self.extract_request_id(user_prompt)

        return has_specific_keyword and request_id is not None

    # Static parsing methods removed - using dynamic multi-endpoint agent only

    def extract_general_field_filters(self, user_prompt):
        """Extract general field filters with contains/includes/in operators"""
        prompt_lower = user_prompt.lower()
        field_filters = []

        import re

        # Pattern: "{field} contains/includes/in {value}"
        # Map common field names to actual property keys
        field_mapping = {
            'assignee': 'request.technicianId',
            'technician': 'request.technicianId',
            'requester': 'request.requesterId',
            'group': 'request.groupId',
            'category': 'request.categoryId',
            'impact': 'request.impactId',
            'urgency': 'request.urgencyId',
            'location': 'request.locationId',
            'department': 'request.departmentId'
        }

        # Pattern: "field contains/includes/in value"
        for field_name, property_key in field_mapping.items():
            patterns = [
                rf'{field_name}\s+(?:contains|includes|in)\s+(\w+)',
                rf'{field_name}\s+(?:is|=|equals?)\s+(\w+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    field_value = match.group(1)

                    # Skip if this is handled by specific extractors
                    if field_name in ['assignee', 'technician']:
                        # Skip all assignee/technician patterns as they're handled by assignment filters
                        continue

                    # Try to convert to ID if it's a number
                    try:
                        field_id = int(field_value)
                        field_filters.append({
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": property_key
                            },
                            "operator": "in",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "ListLongValueRest",
                                    "value": [field_id]
                                }
                            }
                        })
                    except ValueError:
                        # If not a number, use string comparison
                        field_filters.append({
                            "type": "RelationalQualificationRest",
                            "leftOperand": {
                                "type": "PropertyOperandRest",
                                "key": property_key
                            },
                            "operator": "contains",
                            "rightOperand": {
                                "type": "ValueOperandRest",
                                "value": {
                                    "type": "StringValueRest",
                                    "value": field_value
                                }
                            }
                        })

                    break  # Only process first match per field

        return field_filters

    def extract_tag_filters(self, user_prompt):
        """Extract tag-based filters from user prompt"""
        prompt_lower = user_prompt.lower()
        tag_filters = []

        import re

        # Pattern: "tagged with 'tag'" or "has tag 'tag'"
        tag_pattern = r'(?:tagged?\s+with|has\s+tags?|with\s+tags?)\s+["\']([^"\']+)["\']'
        tag_matches = re.findall(tag_pattern, prompt_lower)

        if tag_matches:
            # Multiple tags - all must exist
            tag_filters.append({
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
                        "value": tag_matches
                    }
                }
            })

        # Pattern: "tag contains 'text'"
        tag_contains_pattern = r'tags?\s+(?:contains?|includes?)\s+["\']([^"\']+)["\']'
        tag_contains_match = re.search(tag_contains_pattern, prompt_lower)
        if tag_contains_match:
            tag_filters.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.tags"
                },
                "operator": "Contains",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "StringValueRest",
                        "value": tag_contains_match.group(1)
                    }
                }
            })

        return tag_filters

    def train_from_examples(self, training_examples):
        """Train the agent from comprehensive filter examples"""
        print("🎓 Training agent with comprehensive filter examples...")

        # Store training examples for pattern recognition
        self.training_patterns = {
            'subject_operators': {
                'contains': ['contains', 'has', 'includes'],
                'start_with': ['starts with', 'begins with'],
                'end_with': ['ends with', 'finishes with'],
                'equals': ['is', 'equals', 'exactly'],
                'not_contains': ['does not contain', 'not contains'],
                'is_blank': ['is empty', 'is blank', 'no subject']
            },
            'priority_patterns': {
                'single': r'priority\s+(?:is|as|equals?)\s+(\w+)',
                'negative': r'not\s+(\w+)\s+priority',
                'range': r'(\w+)\s+to\s+(\w+)\s+priority',
                'multiple': r'(?:high|medium|low|urgent)\s+(?:or|and)\s+(?:high|medium|low|urgent)'
            },
            'date_patterns': {
                'within_last': r'(?:in|within|last|past)\s+(\d+)\s+(day|days|week|weeks|month|months)',
                'before': r'before\s+(\d{4}-\d{2}-\d{2})',
                'after': r'after\s+(\d{4}-\d{2}-\d{2})',
                'between': r'between\s+(\d{4}-\d{2}-\d{2})\s+and\s+(\d{4}-\d{2}-\d{2})'
            },
            'field_mappings': {
                'assignee': 'request.technicianId',
                'technician': 'request.technicianId',
                'requester': 'request.requesterId',
                'category': 'request.categoryId',
                'location': 'request.locationId',
                'urgency': 'request.urgencyId',
                'priority': 'request.priorityId',
                'status': 'request.statusId',
                'group': 'request.groupId'
            }
        }

        # Example payload structures for reference
        self.payload_templates = {
            'string_filter': {
                "type": "RelationalQualificationRest",
                "leftOperand": {"key": "{field}", "type": "PropertyOperandRest"},
                "operator": "{operator}",
                "rightOperand": {"type": "ValueOperandRest", "value": {"type": "StringValueRest", "value": "{value}"}}
            },
            'list_filter': {
                "type": "RelationalQualificationRest",
                "leftOperand": {"key": "{field}", "type": "PropertyOperandRest"},
                "operator": "{operator}",
                "rightOperand": {"type": "ValueOperandRest", "value": {"type": "ListLongValueRest", "value": "{values}"}}
            },
            'date_filter': {
                "type": "RelationalQualificationRest",
                "leftOperand": {"key": "{field}", "type": "VariableOperandRest"},
                "operator": "{operator}",
                "rightOperand": {"type": "ValueOperandRest", "value": {"type": "DurationValueRest", "value": "{value}", "unit": "{unit}"}}
            }
        }

        print("✅ Agent training completed with comprehensive filter patterns")

    def validate_and_explain_filters(self, user_prompt, generated_quals):
        """Validate generated filters and provide explanation"""
        explanations = []

        for qual in generated_quals:
            if qual.get("type") == "RelationalQualificationRest":
                field = qual.get("leftOperand", {}).get("key", "unknown")
                operator = qual.get("operator", "unknown")
                value = qual.get("rightOperand", {}).get("value", {})

                # Generate human-readable explanation
                field_name = field.split(".")[-1] if "." in field else field

                if operator == "in":
                    if isinstance(value.get("value"), list):
                        values = value.get("value", [])
                        explanations.append(f"Filter: {field_name} is one of {values}")
                    else:
                        explanations.append(f"Filter: {field_name} equals {value.get('value')}")
                elif operator == "not_in":
                    values = value.get("value", [])
                    explanations.append(f"Filter: {field_name} is NOT one of {values}")
                elif operator == "contains":
                    explanations.append(f"Filter: {field_name} contains '{value.get('value')}'")
                elif operator == "start_with":
                    explanations.append(f"Filter: {field_name} starts with '{value.get('value')}'")
                elif operator == "within_last":
                    duration = value.get("value", 0)
                    unit = value.get("unit", "days")
                    explanations.append(f"Filter: {field_name} within last {duration} {unit}")
                else:
                    explanations.append(f"Filter: {field_name} {operator} {value.get('value')}")

        return {
            "filter_count": len(generated_quals),
            "explanations": explanations,
            "validation_status": "valid" if generated_quals else "no_filters"
        }

    def fetch_specific_request(self, request_id):
        """Fetch specific request by ID"""
        try:
            # Get access token
            auth_token = self.get_access_token()
            if not auth_token:
                return {
                    "success": False,
                    "error": "Failed to obtain access token"
                }

            # Build URL
            url = f"{self.config.REQUEST_DETAIL_URL}/{request_id}"

            # Prepare headers
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'Authorization': f'Bearer {auth_token}',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Referer': f'{self.config.BASE_URL}/t/request/{request_id}',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
            }

            # Make the API call
            response = requests.get(
                url,
                headers=headers,
                verify=False,
                timeout=self.config.REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                request_data = response.json()

                # Extract key information for summary
                summary = {
                    "id": request_data.get("id"),
                    "name": request_data.get("name"),
                    "subject": request_data.get("subject"),
                    "description": request_data.get("description", "").replace("<p>", "").replace("</p>", ""),
                    "status_id": request_data.get("statusId"),
                    "priority_id": request_data.get("priorityId"),
                    "requester": request_data.get("requester"),
                    "requester_name": request_data.get("requesterName"),
                    "created_time": request_data.get("createdTime"),
                    "updated_time": request_data.get("updatedTime"),
                    "due_by": request_data.get("dueBy"),
                    "request_type": request_data.get("requestType"),
                    "tags": request_data.get("tags", [])
                }

                return {
                    "success": True,
                    "data": request_data,
                    "summary": summary,
                    "api_call": {
                        "url": url,
                        "method": "GET",
                        "request_id": request_id
                    },
                    "message": f"Found request {request_data.get('name', request_id)}: {request_data.get('subject', 'No subject')}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Request not found or access denied (status {response.status_code})",
                    "details": response.text,
                    "api_call": {
                        "url": url,
                        "method": "GET",
                        "request_id": request_id
                    }
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching request: {str(e)}",
                "request_id": request_id
            }
    
    def build_advanced_qualification(self, user_prompt):
        """Build qualification using pure multi-endpoint agent NLP - NO STATIC PARSING"""
        print(f"🎯 Processing prompt with dynamic NLP: '{user_prompt}'")

        try:
            # Use ONLY the multi-endpoint agent for all filter generation
            agent_response = self.api_executor.process_request(user_prompt)

            if agent_response and agent_response.get("qualification"):
                qualification = agent_response["qualification"]
                quals = qualification.get("qualDetails", {}).get("quals", [])
                print(f"✅ Multi-endpoint agent generated {len(quals)} dynamic filters")

                # Log the generated filters for debugging
                for i, qual in enumerate(quals):
                    field = qual.get("leftOperand", {}).get("key", "unknown")
                    operator = qual.get("operator", "unknown")
                    value = qual.get("rightOperand", {}).get("value", {}).get("value", "unknown")
                    print(f"   Filter {i+1}: {field} {operator} {value}")

                return qualification
            else:
                print("⚠️ Multi-endpoint agent returned no qualification")
                return {
                    "qualDetails": {
                        "quals": [],
                        "type": "FlatQualificationRest"
                    }
                }
        except Exception as e:
            print(f"❌ Error in multi-endpoint agent: {str(e)}")
            return {
                "qualDetails": {
                    "quals": [],
                    "type": "FlatQualificationRest"
                }
            }
    
    def execute_api_call(self, user_prompt):
        """Execute the API call based on user prompt"""
        try:
            # Check if this is a specific request query
            if self.is_specific_request_query(user_prompt):
                request_id = self.extract_request_id(user_prompt)
                if request_id:
                    return self.fetch_specific_request(request_id)

            # Get fresh access token for search queries
            auth_token = self.get_access_token()
            if not auth_token:
                return {
                    "success": False,
                    "error": "Failed to obtain access token",
                    "details": "Could not authenticate with the API"
                }
            
            # Parse the prompt for basic parameters only
            params = self.parse_user_prompt(user_prompt)

            # Use ONLY multi-endpoint agent for all filter generation
            request_body = self.build_advanced_qualification(user_prompt)

            print(f"🔍 Generated request body: {request_body}")

            # Build URL with query parameters
            query_string = urlencode(params)
            url = f"{self.config.REQUEST_SEARCH_URL}?{query_string}"
            
            # Prepare headers
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'API-Agent/1.0'
            }
            
            # Make the API call
            response = requests.post(
                url,
                headers=headers,
                json=request_body,
                verify=False,  # --insecure equivalent
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            # Parse response
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data,
                    "api_call": {
                        "url": url,
                        "method": "POST",
                        "request_body": request_body,
                        "parameters": params
                    },
                    "message": f"Found {len(data.get('content', []))} requests" if isinstance(data, dict) and 'content' in data else "API call successful"
                }
            else:
                error_message = f"API call failed with status {response.status_code}"
                if response.status_code == 502:
                    error_message += " - Server error (Bad Gateway)"
                elif response.status_code == 500:
                    error_message += " - Internal server error"
                elif response.status_code == 404:
                    error_message += " - Endpoint not found"
                elif response.status_code == 401:
                    error_message += " - Authentication failed"
                elif response.status_code == 403:
                    error_message += " - Access forbidden"

                return {
                    "success": False,
                    "error": error_message,
                    "details": response.text[:500] + "..." if len(response.text) > 500 else response.text,
                    "api_call": {
                        "url": url,
                        "method": "POST",
                        "request_body": request_body,
                        "priority_filter": priority_ids,
                        "status_filter": status_ids
                    },
                    "troubleshooting": {
                        "status_mapping_available": len(self.status_mapping) > 0,
                        "status_mapping": dict(list(self.status_mapping.items())[:5]) if self.status_mapping else {},
                        "filters_applied": {
                            "priority": priority_ids,
                            "status": status_ids
                        }
                    }
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "api_call": {
                    "url": url if 'url' in locals() else "URL not built",
                    "method": "POST"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

# Initialize the executor
executor = APIExecutor()

@app.route('/execute-request', methods=['POST'])
def execute_request():
    """
    Execute API request based on user prompt

    Request body: {"request": "Get all the request with priority as low"}
    """
    try:
        # Get request data
        data = request.get_json()

        if not data or 'request' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'request' field in JSON body",
                "example": {"request": "Get all the request with priority as low"}
            }), 400

        user_prompt = data['request']

        # Execute using multi-endpoint agent with fallback to original agent
        try:
            # Try multi-endpoint agent first
            multi_result = executor.multi_agent.execute_query(user_prompt)

            # Check if qualification was generated successfully
            qualification_generated = (
                'qualification' in multi_result and
                multi_result['qualification'] and
                'qualDetails' in multi_result['qualification'] and
                'quals' in multi_result['qualification']['qualDetails']
            )

            # Format the result to match original format
            if qualification_generated:
                # Qualification generated successfully - return 200
                result = {
                    "success": True,
                    "endpoint_used": multi_result['endpoint'],
                    "qualification": multi_result['qualification'],
                    "user_prompt": user_prompt,
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                }

                # Check if API execution was successful
                if 'error' not in multi_result['response']:
                    # API execution successful - include data
                    api_response = multi_result['response']
                    result.update({
                        "total_count": api_response.get('totalCount', len(api_response) if isinstance(api_response, list) else 0),
                        "data": api_response.get('objectList', api_response if isinstance(api_response, list) else [])
                    })
                    print(f"✅ API execution successful - returned {result['total_count']} records")
                else:
                    # API execution failed but qualification was generated
                    result["api_execution_note"] = "Qualification generated successfully, but API execution failed"
                    result["api_error"] = multi_result['response']['error']
                    result["total_count"] = 0
                    result["data"] = []
                    print(f"⚠️ API execution failed: {multi_result['response']['error']}")
            else:
                # No qualification generated - this is an actual error
                result = {
                    "success": False,
                    "error": multi_result['response'].get('error', 'Failed to generate qualification'),
                    "endpoint_used": multi_result['endpoint'],
                    "user_prompt": user_prompt,
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                }
        except Exception as e:
            print(f"⚠️ Multi-endpoint failed, falling back to original agent: {str(e)}")
            # Fallback to original agent
            result = executor.execute_api_call(user_prompt)
        
        # Add metadata
        result['user_prompt'] = user_prompt
        result['timestamp'] = __import__('datetime').datetime.now().isoformat()
        
        # Return appropriate status code
        status_code = 200 if result['success'] else 500
        # Return appropriate status code
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 500, status_code
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "API Endpoint Server",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })

@app.route('/examples', methods=['GET'])
def get_examples():
    """Get example requests"""
    examples = [
        {
            "description": "Get low priority requests",
            "request": {"request": "Get all the request with priority as low"}
        },
        {
            "description": "Get medium priority requests",
            "request": {"request": "Show me medium priority requests"}
        },
        {
            "description": "Get high and urgent requests",
            "request": {"request": "Find high and urgent priority requests"}
        },
        {
            "description": "Get all active requests (no priority filter)",
            "request": {"request": "Get all active requests"}
        },
        {
            "description": "Get requests with specific status",
            "request": {"request": "Get all tickets that have status as in progress"}
        },
        {
            "description": "Get open requests",
            "request": {"request": "Show me all open requests"}
        },
        {
            "description": "Get specific request by ID",
            "request": {"request": "Get request 2"}
        },
        {
            "description": "Get request details by name",
            "request": {"request": "Show me details of request INC-2"}
        },
        {
            "description": "Text search in subject",
            "request": {"request": "Get all requests with subject contains 'urgent'"}
        },
        {
            "description": "Date-based filtering",
            "request": {"request": "Show me requests created today"}
        },
        {
            "description": "Assignment filtering",
            "request": {"request": "Get all unassigned requests"}
        },
        {
            "description": "Tag-based filtering",
            "request": {"request": "Find requests tagged with 'hardware'"}
        },
        {
            "description": "Complex combination",
            "request": {"request": "Get high priority unassigned requests created last week"}
        }
    ]

    multi_endpoint_examples = [
        {
            "description": "Urgency-based filtering (auto-resolves urgency names)",
            "request": {"request": "Get all requests with urgency as high"}
        },
        {
            "description": "User assignment with name resolution",
            "request": {"request": "Get all requests assigned to AutoMind"}
        },
        {
            "description": "Service catalog search",
            "request": {"request": "Show me all service catalogs for employee onboarding"}
        },
        {
            "description": "User details lookup",
            "request": {"request": "Get user details for all technicians"}
        },
        {
            "description": "Urgency levels mapping",
            "request": {"request": "Show me all urgency levels"}
        },
        {
            "description": "Service catalog with specific name",
            "request": {"request": "Find service catalog named laptop"}
        }
    ]

    return jsonify({
        "examples": examples + multi_endpoint_examples,
        "endpoint": "/execute-request",
        "description": "Unified endpoint with multi-endpoint detection and auto-resolution",
        "features": [
            "Automatic endpoint detection (requests, urgency, service_catalog, users)",
            "User name to ID resolution",
            "Urgency level to ID resolution",
            "Service catalog name resolution",
            "Smart qualification building",
            "Fallback to original agent if needed"
        ],
        "method": "POST"
    })

@app.route('/endpoints', methods=['GET'])
def get_endpoints():
    """Get comprehensive information about all known endpoints that the agent can handle"""

    # Get dynamic endpoint information from the multi-endpoint agent
    try:
        # Access the multi-endpoint agent through the API executor
        multi_agent = executor.multi_agent

        # Get endpoint detection patterns and capabilities
        endpoint_info = {
            "timestamp": datetime.now().isoformat(),
            "agent_version": "Enhanced Multi-Value Filter Agent v2.0",
            "total_endpoints": 4,
            "available_endpoints": [
                {
                    "name": "requests",
                    "endpoint_id": "requests",
                    "api_url": "https://172.16.15.113/api/request/search/byqual",
                    "method": "POST",
                    "description": "Search and filter IT service requests with advanced multi-value filtering",
                    "primary_use_cases": [
                        "Search requests by status, priority, urgency",
                        "Filter by assignee, requester, category",
                        "Text search in subject, description",
                        "Date-based filtering",
                        "Complex multi-value combinations"
                    ],
                    "supported_filters": {
                        "status": {
                            "type": "multi-value",
                            "operators": ["in", "not_in"],
                            "values": ["open", "in progress", "pending", "testing", "resolved", "closed"],
                            "business_logic": ["active", "unresolved", "completed"],
                            "examples": ["status is open and in progress", "except closed and resolved"]
                        },
                        "priority": {
                            "type": "multi-value",
                            "operators": ["in", "not_in"],
                            "values": ["low", "medium", "high", "urgent", "critical"],
                            "examples": ["priority high and urgent", "not low priority"]
                        },
                        "urgency": {
                            "type": "single-value",
                            "operators": ["in"],
                            "values": ["low", "medium", "high", "urgent"],
                            "examples": ["urgency is high"]
                        },
                        "assignee": {
                            "type": "multi-value",
                            "operators": ["in", "not_in"],
                            "auto_resolution": "user names to IDs",
                            "examples": ["assigned to Tech1 and Tech2", "not assigned to Admin"]
                        },
                        "requester": {
                            "type": "text-search",
                            "operators": ["contains", "equals"],
                            "auto_resolution": "user names to IDs",
                            "examples": ["requester contains John"]
                        },
                        "text_search": {
                            "type": "text-search",
                            "fields": ["subject", "description"],
                            "operators": ["contains", "starts_with", "ends_with"],
                            "examples": ["subject contains error", "description has network"]
                        },
                        "date_filters": {
                            "type": "temporal",
                            "operators": ["within_last", "between", "after", "before"],
                            "examples": ["created today", "last 7 days", "between 2024-01-01 and 2024-01-31"]
                        },
                        "business_logic": {
                            "type": "special",
                            "vip_customers": "vipRequest = True",
                            "escalated": "slaViolated = True",
                            "recent": "within last 3 days",
                            "examples": ["VIP customers", "escalated requests", "recent tickets"]
                        }
                    },
                    "detection_keywords": ["request", "ticket", "incident", "search", "find", "get", "show", "list"],
                    "sample_queries": [
                        "Get me all requests where status is open and in progress",
                        "Show requests with high priority except closed",
                        "Find tickets assigned to Tech1 created today",
                        "List VIP customer requests with urgent priority",
                        "Search requests containing 'network' in subject"
                    ]
                },
                {
                    "name": "urgency",
                    "endpoint_id": "urgency",
                    "api_url": "https://172.16.15.113/api/urgency/search/byqual",
                    "method": "POST",
                    "description": "Get urgency levels mapping and information",
                    "primary_use_cases": [
                        "Get all available urgency levels",
                        "Map urgency names to IDs",
                        "Understand urgency hierarchy"
                    ],
                    "supported_filters": {
                        "basic_search": {
                            "type": "general",
                            "description": "Returns all urgency levels with ID mappings"
                        }
                    },
                    "detection_keywords": ["urgency", "urgent", "priority level"],
                    "sample_queries": [
                        "Get all urgency levels",
                        "Show urgency mapping",
                        "What urgency levels are available?"
                    ],
                    "returns": {
                        "format": "List of urgency objects",
                        "fields": ["id", "name", "description", "level"]
                    }
                },
                {
                    "name": "service_catalog",
                    "endpoint_id": "service_catalog",
                    "api_url": "https://172.16.15.113/api/service_catalog/search/byqual",
                    "method": "POST",
                    "description": "Search service catalog items and services",
                    "primary_use_cases": [
                        "Search available services",
                        "Filter by service category",
                        "Find services by name or description"
                    ],
                    "supported_filters": {
                        "category": {
                            "type": "single-value",
                            "operators": ["in", "contains"],
                            "examples": ["category IT", "category contains Hardware"]
                        },
                        "name": {
                            "type": "text-search",
                            "operators": ["contains", "starts_with"],
                            "examples": ["name contains laptop", "service starts with Email"]
                        },
                        "status": {
                            "type": "single-value",
                            "operators": ["in"],
                            "values": ["active", "inactive"],
                            "examples": ["status active"]
                        }
                    },
                    "detection_keywords": ["service", "catalog", "offering", "available services"],
                    "sample_queries": [
                        "Get all services in IT category",
                        "Find services containing 'email'",
                        "Show active service catalog items"
                    ]
                },
                {
                    "name": "users",
                    "endpoint_id": "users",
                    "api_url": "https://172.16.15.113/api/technician/active/list",
                    "method": "GET",
                    "description": "Get active technicians and users list",
                    "primary_use_cases": [
                        "Get all active technicians",
                        "User name to ID mapping",
                        "Available assignees list"
                    ],
                    "supported_filters": {
                        "active_only": {
                            "type": "boolean",
                            "description": "Returns only active users",
                            "default": True
                        }
                    },
                    "detection_keywords": ["user", "technician", "assignee", "staff", "team member"],
                    "sample_queries": [
                        "Get all users",
                        "Show active technicians",
                        "List available assignees",
                        "Who can I assign tickets to?"
                    ],
                    "returns": {
                        "format": "List of user objects",
                        "fields": ["id", "name", "email", "role", "active"]
                    }
                }
            ],
            "agent_capabilities": {
                "multi_value_filters": {
                    "description": "Supports multiple values in single filter",
                    "operators": ["in", "not_in"],
                    "examples": ["status is open, pending, in progress", "except closed and resolved"]
                },
                "auto_resolution": {
                    "user_names": "Automatically resolves user names to IDs using fuzzy matching",
                    "urgency_levels": "Maps urgency names (low, medium, high, urgent) to system IDs",
                    "service_catalogs": "Resolves service names to catalog IDs",
                    "status_mapping": "Maps status names to system status IDs with business logic"
                },
                "business_logic": {
                    "shortcuts": {
                        "active": "open + in progress",
                        "unresolved": "open + in progress + pending",
                        "completed": "resolved + closed"
                    },
                    "special_filters": ["VIP customers", "escalated requests", "recent items"]
                },
                "natural_language": {
                    "compound_queries": "Handles 'and', 'or', comma-separated values",
                    "exclusion_patterns": "Supports 'except', 'not', 'excluding' patterns",
                    "temporal_expressions": "Understands 'today', 'last week', 'recent', date ranges"
                },
                "validation": {
                    "conflict_detection": "Detects conflicting filter combinations",
                    "value_validation": "Validates data types and ranges",
                    "large_sets": "Handles up to 1000 values per filter"
                }
            },
            "endpoint_detection": {
                "algorithm": "Keyword-based scoring with context analysis",
                "fallback": "Defaults to 'requests' endpoint for ambiguous queries",
                "confidence_threshold": "Minimum score of 1 for endpoint selection"
            }
        }

        return jsonify(endpoint_info)

    except Exception as e:
        # Fallback to static information if dynamic retrieval fails
        return jsonify({
            "error": "Could not retrieve dynamic endpoint information",
            "fallback_info": {
                "available_endpoints": ["requests", "urgency", "service_catalog", "users"],
                "primary_endpoint": "requests",
                "description": "Multi-endpoint API agent with dynamic filter generation"
            },
            "error_details": str(e)
        })

if __name__ == '__main__':
    print("🚀 Starting Unified Multi-Endpoint API Server...")
    print("📡 Main Endpoint: POST /execute-request")
    print("🎯 Features:")
    print("   • Automatic endpoint detection")
    print("   • User name resolution")
    print("   • Urgency level resolution")
    print("   • Service catalog resolution")
    print("   • Smart qualification building")
    print("📋 Example: {\"request\": \"Get all requests with urgency as high\"}")
    print("🔗 Health check: GET /health")
    print("📚 Examples: GET /examples")
    print("🔧 Endpoints info: GET /endpoints")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
