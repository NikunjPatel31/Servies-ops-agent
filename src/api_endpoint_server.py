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
        """Get status mapping from the API"""
        try:
            # Return cached mapping if available
            if self.status_mapping_loaded:
                return self.status_mapping

            print("📋 Fetching status mapping...")

            # Get access token
            auth_token = self.get_access_token()
            if not auth_token:
                print("❌ Cannot fetch status mapping - no auth token")
                return {}

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
                        return {}

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
                    return {}

                self.status_mapping_loaded = True
                print(f"✅ Status mapping loaded: {len(self.status_mapping)} statuses")
                print(f"   Available statuses: {list(self.status_mapping.keys())}")

                return self.status_mapping
            else:
                print(f"❌ Status API failed: {response.status_code} - {response.text}")
                return {}

        except Exception as e:
            print(f"❌ Status mapping error: {str(e)}")
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
    
    def build_request_body(self, priority_ids=None, status_ids=None):
        """Build the request body for the API call"""
        quals = []

        # Handle status filtering
        if status_ids:
            # If specific statuses are requested, use them
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
            # Default: exclude closed requests (status ID 13)
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

        # Add priority filter if specified
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
            # Get fresh access token
            auth_token = self.get_access_token()
            if not auth_token:
                return {
                    "success": False,
                    "error": "Failed to obtain access token",
                    "details": "Could not authenticate with the API"
                }
            
            # Parse the prompt
            params = self.parse_user_prompt(user_prompt)
            priority_ids = self.extract_priority_filter(user_prompt)
            status_ids = self.extract_status_filter(user_prompt)

            # Build request body
            request_body = self.build_request_body(priority_ids, status_ids)
            
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
                return {
                    "success": False,
                    "error": f"API call failed with status {response.status_code}",
                    "details": response.text,
                    "api_call": {
                        "url": url,
                        "method": "POST",
                        "request_body": request_body,
                        "priority_filter": priority_ids,
                        "status_filter": status_ids
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

        # Execute the API call (token is obtained automatically)
        result = executor.execute_api_call(user_prompt)
        
        # Add metadata
        result['user_prompt'] = user_prompt
        result['timestamp'] = __import__('datetime').datetime.now().isoformat()
        
        # Return appropriate status code
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
        
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
        }
    ]
    
    return jsonify({
        "examples": examples,
        "endpoint": "/execute-request",
        "method": "POST"
    })

if __name__ == '__main__':
    print("🚀 Starting API Endpoint Server...")
    print("📡 Endpoint: POST /execute-request")
    print("📋 Example: {\"request\": \"Get all the request with priority as low\"}")
    print("🔗 Health check: GET /health")
    print("📚 Examples: GET /examples")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
