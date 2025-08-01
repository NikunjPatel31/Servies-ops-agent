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
    
    def extract_priority_filter(self, user_prompt):
        """Extract priority filter from user prompt"""
        prompt_lower = user_prompt.lower()
        
        priority_ids = []
        for priority_name, priority_id in self.config.PRIORITY_MAPPING.items():
            if priority_name in prompt_lower:
                priority_ids.append(priority_id)
        
        return priority_ids

    def extract_status_filter(self, user_prompt):
        """Extract status filter from user prompt"""
        prompt_lower = user_prompt.lower()

        # Get status mapping
        status_mapping = self.get_status_mapping()
        if not status_mapping:
            return []

        status_ids = []

        # Check for specific status mentions
        for status_name, status_id in status_mapping.items():
            if status_name in prompt_lower:
                status_ids.append(status_id)

        # Remove duplicates
        status_ids = list(set(status_ids))

        return status_ids

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

    def extract_text_search(self, user_prompt):
        """Extract text search terms from user prompt"""
        prompt_lower = user_prompt.lower()
        text_searches = {}

        # Look for patterns like "subject contains", "description has", etc.
        import re

        # Pattern: "subject contains 'text'" or "subject has 'text'" (with quotes)
        subject_pattern_quoted = r'subject\s+(?:contains|has|includes|with)\s+["\']([^"\']+)["\']'
        subject_match_quoted = re.search(subject_pattern_quoted, prompt_lower)
        if subject_match_quoted:
            text_searches['subject'] = subject_match_quoted.group(1)

        # Pattern: "subject contains text" (without quotes)
        elif 'subject' in prompt_lower and any(op in prompt_lower for op in ['contains', 'has', 'includes', 'with']):
            subject_pattern_unquoted = r'subject\s+(?:contains|has|includes|with)\s+(\w+)'
            subject_match_unquoted = re.search(subject_pattern_unquoted, prompt_lower)
            if subject_match_unquoted:
                text_searches['subject'] = subject_match_unquoted.group(1)

        # Pattern: "description contains 'text'" (with quotes)
        desc_pattern_quoted = r'description\s+(?:contains|has|includes|with)\s+["\']([^"\']+)["\']'
        desc_match_quoted = re.search(desc_pattern_quoted, prompt_lower)
        if desc_match_quoted:
            text_searches['description'] = desc_match_quoted.group(1)

        # Pattern: "description contains text" (without quotes)
        elif 'description' in prompt_lower and any(op in prompt_lower for op in ['contains', 'has', 'includes', 'with']):
            desc_pattern_unquoted = r'description\s+(?:contains|has|includes|with)\s+(\w+)'
            desc_match_unquoted = re.search(desc_pattern_unquoted, prompt_lower)
            if desc_match_unquoted:
                text_searches['description'] = desc_match_unquoted.group(1)

        # Pattern: "name contains 'text'" or "title contains 'text'" (with quotes)
        name_pattern_quoted = r'(?:name|title)\s+(?:contains|has|includes|with)\s+["\']([^"\']+)["\']'
        name_match_quoted = re.search(name_pattern_quoted, prompt_lower)
        if name_match_quoted:
            text_searches['name'] = name_match_quoted.group(1)

        # Pattern: "name contains text" (without quotes)
        elif any(field in prompt_lower for field in ['name', 'title']) and any(op in prompt_lower for op in ['contains', 'has', 'includes', 'with']):
            name_pattern_unquoted = r'(?:name|title)\s+(?:contains|has|includes|with)\s+(\w+)'
            name_match_unquoted = re.search(name_pattern_unquoted, prompt_lower)
            if name_match_unquoted:
                text_searches['name'] = name_match_unquoted.group(1)

        # General text search without field specification
        if not text_searches:
            # Only look for explicit text search patterns, not general "with" usage
            # Look for "contains text", "having text", "includes text" but NOT "with status/priority"
            text_search_patterns = [
                r'contains\s+(\w+)',
                r'having\s+(\w+)',
                r'includes\s+(\w+)'
            ]

            for pattern in text_search_patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    search_term = match.group(1)

                    # Skip assignment-related terms and status-related terms
                    skip_terms = ['unassigned', 'assigned', 'technician', 'status', 'priority']

                    # Also skip if this appears to be a field-specific pattern
                    field_context_patterns = [
                        r'assignee\s+(?:contains|includes|in)\s+' + re.escape(search_term),
                        r'technician\s+(?:contains|includes|in)\s+' + re.escape(search_term),
                        r'group\s+(?:contains|includes|in)\s+' + re.escape(search_term),
                        r'category\s+(?:contains|includes|in)\s+' + re.escape(search_term),
                        r'requester\s+(?:contains|includes|in)\s+' + re.escape(search_term),
                        r'impact\s+(?:contains|includes|in)\s+' + re.escape(search_term),
                        r'urgency\s+(?:contains|includes|in)\s+' + re.escape(search_term)
                    ]

                    is_field_context = any(re.search(fp, prompt_lower) for fp in field_context_patterns)

                    if search_term not in skip_terms and not is_field_context:
                        # Default to subject search
                        text_searches['subject'] = search_term
                        break

        return text_searches

    def extract_date_filters(self, user_prompt):
        """Extract date-based filters from user prompt"""
        prompt_lower = user_prompt.lower()
        date_filters = []

        import datetime
        import re

        # Common date patterns
        if 'today' in prompt_lower:
            today = datetime.datetime.now().strftime('%Y-%m-%dT00:00:00Z')
            date_filters.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.createdTime"
                },
                "operator": "GreaterThanOrEqual",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "TimeValueRest",
                        "value": today
                    }
                }
            })

        elif 'yesterday' in prompt_lower:
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z')
            date_filters.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.createdTime"
                },
                "operator": "GreaterThanOrEqual",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "TimeValueRest",
                        "value": yesterday
                    }
                }
            })

        elif 'last week' in prompt_lower or 'past week' in prompt_lower:
            last_week = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%dT00:00:00Z')
            date_filters.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.createdTime"
                },
                "operator": "GreaterThanOrEqual",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "TimeValueRest",
                        "value": last_week
                    }
                }
            })

        elif 'last month' in prompt_lower or 'past month' in prompt_lower:
            last_month = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%dT00:00:00Z')
            date_filters.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.createdTime"
                },
                "operator": "GreaterThanOrEqual",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "TimeValueRest",
                        "value": last_month
                    }
                }
            })

        # Pattern for "last X days"
        days_pattern = r'last\s+(\d+)\s+days?'
        days_match = re.search(days_pattern, prompt_lower)
        if days_match:
            days = int(days_match.group(1))
            past_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%dT00:00:00Z')
            date_filters.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.createdTime"
                },
                "operator": "GreaterThanOrEqual",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "TimeValueRest",
                        "value": past_date
                    }
                }
            })

        return date_filters

    def extract_assignment_filters(self, user_prompt):
        """Extract assignment-related filters from user prompt"""
        prompt_lower = user_prompt.lower()
        assignment_filters = []

        import re

        # Pattern 1: "assignee contains/includes/in {value}" - use 'in' operator
        assignee_value_patterns = [
            r'assignee\s+(?:contains|includes|in)\s+(\w+)',
            r'technician\s+(?:contains|includes|in)\s+(\w+)',
            r'assigned\s+to\s+(\w+)',
            r'assignee\s+(?:is|=|equals?)\s+(\w+)'
        ]

        for pattern in assignee_value_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                assignee_value = match.group(1)

                # Map assignee values to IDs
                assignee_mapping = {
                    'unassigned': 0,  # "unassigned" maps to ID 0, not null
                    'none': 0,
                    'null': 0,
                    '0': 0,
                    '1': 1,
                    '2': 2,
                    '3': 3,
                    '4': 4,
                    '5': 5
                }

                # Check if it's a mapped value or try to convert to int
                if assignee_value in assignee_mapping:
                    assignee_id = assignee_mapping[assignee_value]
                else:
                    try:
                        assignee_id = int(assignee_value)
                    except ValueError:
                        # If not a number, look up user by name
                        print(f"🔍 Looking up user: {assignee_value}")
                        user_mapping = self.get_user_mapping()

                        # Try to find user by name (case-insensitive)
                        assignee_value_lower = assignee_value.lower()
                        if assignee_value_lower in user_mapping:
                            assignee_id = user_mapping[assignee_value_lower]
                            print(f"✅ Found user '{assignee_value}' with ID: {assignee_id}")
                        else:
                            # Try partial matching
                            matching_users = {name: uid for name, uid in user_mapping.items()
                                            if assignee_value_lower in name}

                            if matching_users:
                                # Use the first match
                                matched_name, assignee_id = next(iter(matching_users.items()))
                                print(f"✅ Found partial match '{matched_name}' with ID: {assignee_id}")
                            else:
                                print(f"❌ User '{assignee_value}' not found in user mapping")
                                print(f"   Available users: {list(user_mapping.keys())[:10]}")
                                # Fallback to string search in requesterName
                                assignment_filters.append({
                                    "type": "RelationalQualificationRest",
                                    "leftOperand": {
                                        "type": "PropertyOperandRest",
                                        "key": "request.requesterName"
                                    },
                                    "operator": "contains",
                                    "rightOperand": {
                                        "type": "ValueOperandRest",
                                        "value": {
                                            "type": "StringValueRest",
                                            "value": assignee_value
                                        }
                                    }
                                })
                                return assignment_filters

                # Always use RelationalQualificationRest with 'in' operator for ID-based searches
                assignment_filters.append({
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
                            "value": [assignee_id]
                        }
                    }
                })
                return assignment_filters

        # Pattern 2: General unassigned patterns (fallback) - only for simple cases
        # Only use is_null for very specific unassigned patterns that don't use "contains/includes/in"
        simple_unassigned_patterns = [
            'get all unassigned', 'show unassigned', 'find unassigned',
            'not assigned', 'no technician', 'without technician'
        ]

        if any(pattern in prompt_lower for pattern in simple_unassigned_patterns):
            assignment_filters.append({
                "type": "UnaryQualificationRest",
                "operand": {
                    "type": "PropertyOperandRest",
                    "key": "request.technicianId"
                },
                "operator": "is_null"
            })

        # Pattern 3: General assigned patterns (fallback)
        elif any(keyword in prompt_lower for keyword in ['has technician', 'with technician']) and 'contains' not in prompt_lower and 'includes' not in prompt_lower:
            assignment_filters.append({
                "type": "UnaryQualificationRest",
                "operand": {
                    "type": "PropertyOperandRest",
                    "key": "request.technicianId"
                },
                "operator": "is_not_null"
            })

        return assignment_filters

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
        """Build advanced qualification based on natural language prompt"""
        prompt_lower = user_prompt.lower()

        # Extract different types of filters
        priority_ids = self.extract_priority_filter(user_prompt)
        status_ids = self.extract_status_filter(user_prompt)

        # Extract text search terms
        text_search = self.extract_text_search(user_prompt)

        # Extract date filters
        date_filters = self.extract_date_filters(user_prompt)

        # Extract assignment filters
        assignment_filters = self.extract_assignment_filters(user_prompt)

        # Extract tag filters
        tag_filters = self.extract_tag_filters(user_prompt)

        # Extract general field filters
        general_field_filters = self.extract_general_field_filters(user_prompt)

        # Build qualification list
        quals = []

        # Handle status filtering - only add if user specified status OR no status specified
        if status_ids:
            # User specified specific status(es) - use only those
            quals.append({
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
                        "value": status_ids
                    }
                }
            })
        else:
            # No specific status mentioned - check if we should add default filter
            # Only add default "exclude closed" if no other specific filters are present
            has_other_filters = (priority_ids or text_search or date_filters or
                               assignment_filters or tag_filters or general_field_filters)

            if not has_other_filters:
                # No filters at all - add default exclude closed
                quals.append({
                    "type": "RelationalQualificationRest",
                    "leftOperand": {
                        "type": "PropertyOperandRest",
                        "key": "request.statusId"
                    },
                    "operator": "not_in",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {
                            "type": "ListLongValueRest",
                            "value": [self.config.CLOSED_STATUS_ID]
                        }
                    }
                })
            # If other filters are present, don't add default status filter

        # Add priority filter
        if priority_ids:
            quals.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.priorityId"
                },
                "operator": "in",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "ListLongValueRest",
                        "value": priority_ids
                    }
                }
            })

        # Add text search filters
        if text_search:
            for field, search_term in text_search.items():
                quals.append({
                    "type": "RelationalQualificationRest",
                    "leftOperand": {
                        "type": "PropertyOperandRest",
                        "key": f"request.{field}"
                    },
                    "operator": "contains",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {
                            "type": "StringValueRest",
                            "value": search_term
                        }
                    }
                })

        # Add date filters
        for date_filter in date_filters:
            quals.append(date_filter)

        # Add assignment filters
        for assignment_filter in assignment_filters:
            quals.append(assignment_filter)

        # Add tag filters
        for tag_filter in tag_filters:
            quals.append(tag_filter)

        # Add general field filters
        for field_filter in general_field_filters:
            quals.append(field_filter)

        return {
            "qualDetails": {
                "type": "FlatQualificationRest",
                "quals": quals
            }
        }

    def build_request_body(self, priority_ids=None, status_ids=None):
        """Build the request body for the API call (legacy method)"""
        quals = []

        # Handle status filtering
        if status_ids:
            quals.append({
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
                        "value": status_ids
                    }
                }
            })
        else:
            # Default: exclude closed requests
            quals.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.statusId"
                },
                "operator": "not_in",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "ListLongValueRest",
                        "value": [self.config.CLOSED_STATUS_ID]
                    }
                }
            })

        # Add priority filter
        if priority_ids:
            quals.append({
                "type": "RelationalQualificationRest",
                "leftOperand": {
                    "type": "PropertyOperandRest",
                    "key": "request.priorityId"
                },
                "operator": "in",
                "rightOperand": {
                    "type": "ValueOperandRest",
                    "value": {
                        "type": "ListLongValueRest",
                        "value": priority_ids
                    }
                }
            })

        return {
            "qualDetails": {
                "type": "FlatQualificationRest",
                "quals": quals
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
            
            # Parse the prompt
            params = self.parse_user_prompt(user_prompt)

            # Extract filters for response metadata
            priority_ids = self.extract_priority_filter(user_prompt)
            status_ids = self.extract_status_filter(user_prompt)

            # Use advanced qualification builder for complex queries
            request_body = self.build_advanced_qualification(user_prompt)
            
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
                        "priority_filter": priority_ids,
                        "status_filter": status_ids,
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
    """Get available endpoints information"""
    return jsonify({
        "available_endpoints": [
            {
                "name": "requests",
                "url": "/api/request/search/byqual",
                "description": "Search and filter IT service requests",
                "supported_filters": ["status", "priority", "urgency", "assignee", "requester", "category", "subject", "description", "tags", "date"]
            },
            {
                "name": "urgency",
                "url": "/api/urgency/search/byqual",
                "description": "Get urgency levels mapping",
                "supported_filters": []
            },
            {
                "name": "service_catalog",
                "url": "/api/service_catalog/search/byqual",
                "description": "Search service catalog items",
                "supported_filters": ["category", "status", "name", "description"]
            },
            {
                "name": "users",
                "url": "/api/technician/active/list",
                "description": "Get active technicians/users list",
                "supported_filters": []
            }
        ],
        "auto_resolution": {
            "user_names": "Automatically resolves user names to IDs",
            "urgency_levels": "Automatically resolves urgency names to IDs",
            "service_catalogs": "Automatically resolves service catalog names to IDs"
        }
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
