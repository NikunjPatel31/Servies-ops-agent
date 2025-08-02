#!/usr/bin/env python3
"""
Enhanced Multi-Endpoint Agent with LLM Integration
Replaces regex-based filtering with intelligent LLM understanding
"""

import json
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from dynamic_llm_agent import DynamicLLMAgent
from local_intelligence_agent import LocalIntelligenceAgent
from llama_agent import Llama32Agent

class EnhancedMultiEndpointAgent:
    def __init__(self,
                 openai_api_key: str = None,
                 llm_type: str = "auto",
                 llama_endpoint: str = None,
                 llama_model: str = "llama3.2"):
        """
        Initialize Enhanced Multi-Endpoint Agent

        Args:
            openai_api_key: OpenAI API key (for GPT-4)
            llm_type: "openai", "llama", "auto", or "llama_only" (Llama-only mode)
            llama_endpoint: Llama API endpoint (e.g., Ollama)
            llama_model: Llama model name
        """
        # Use the same working config as demo agent
        self.base_url = "https://172.16.15.113"
        self.auth_token = None
        self.username = "automind@motadata.com"
        self.password = "2d7QdRn6bMI1Q2vQBhficw=="
        self.client_auth = "Basic ZmxvdG8td2ViLWFwcDpjN3ByZE5KRVdFQmt4NGw3ZmV6bA=="

        # Create config object for compatibility
        class Config:
            def __init__(self, base_url, username, password, client_auth):
                self.base_url = base_url
                self.username = username
                self.password = password
                self.client_auth = client_auth
                self.auth_token = None

            def get_headers(self):
                """Get authentication headers for API requests"""
                if not self.auth_token:
                    self._get_access_token()

                return {
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                }

            def _get_access_token(self):
                """Get access token for API authentication"""
                import requests

                # Use correct OAuth endpoint
                token_url = "http://172.16.15.113/api/oauth/token"

                headers = {
                    'Accept': '*/*',
                    'Accept-Language': 'en-GB,en;q=0.9',
                    'Authorization': 'Basic ZmxvdG8td2ViLWFwcDpjN3ByZE5KRVdFQmt4NGw3ZmV6bA==',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'http://172.16.15.113',
                    'Referer': 'http://172.16.15.113/login?redirectFrom=%2Ft%2Frequest%2F',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
                }

                # Use URL-encoded format as shown in curl
                data = 'username=automind%40motadata.com&password=2d7QdRn6bMI1Q2vQBhficw%3D%3D&grant_type=password'

                try:
                    response = requests.post(token_url, headers=headers, data=data, verify=False)
                    if response.status_code == 200:
                        token_data = response.json()
                        self.auth_token = token_data.get("access_token")
                        print("✅ Config token obtained successfully")
                    else:
                        print(f"❌ Config token request failed: {response.status_code}")
                except Exception as e:
                    print(f"❌ Config token request error: {e}")

        self.config = Config(self.base_url, self.username, self.password, self.client_auth)

        # Check for Llama-only mode
        self.llama_only_mode = (llm_type == "llama_only")
        if self.llama_only_mode:
            print("🦙 LLAMA-ONLY MODE: No fallbacks will be used")
            llm_type = "llama"  # Convert to regular llama for detection

        # Initialize intelligent agents based on availability
        self.llm_type = self._detect_llm_type(llm_type, openai_api_key, llama_endpoint)

        if self.llm_type == "llama":
            self.llm_agent = Llama32Agent(
                deployment_type="ollama",
                api_endpoint=llama_endpoint,
                model_name=llama_model
            )
            print(f"🦙 Using Llama 3.2 LLM: {llama_model}")
        elif self.llm_type == "openai":
            self.llm_agent = DynamicLLMAgent(openai_api_key)
            print("🤖 Using OpenAI GPT-4 LLM")
        else:
            self.llm_agent = None
            print("⚠️ No LLM available, using local intelligence only")

        self.local_agent = LocalIntelligenceAgent()

        # Cache for dynamic mappings
        self.mappings_cache = {}
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 minutes

        print("🚀 Enhanced Multi-Endpoint Agent initialized with LLM intelligence")

    def _detect_llm_type(self, llm_type: str, openai_api_key: str, llama_endpoint: str) -> str:
        """Detect which LLM to use based on availability"""
        if llm_type == "llama" or llm_type == "llama_only":
            return "llama"
        elif llm_type == "openai":
            return "openai"
        elif llm_type == "auto":
            # Auto-detect based on availability
            # Check for Llama endpoint first (prefer local)
            if llama_endpoint or self._test_ollama_connection():
                return "llama"
            elif openai_api_key or os.getenv("OPENAI_API_KEY"):
                return "openai"
            else:
                return "none"
        else:
            return "none"

    def _test_ollama_connection(self) -> bool:
        """Test if Ollama is available locally"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def execute_request(self, user_prompt: str) -> Dict[str, Any]:
        """Execute user request with LLM-powered understanding"""
        try:
            print(f"🎯 Processing request: '{user_prompt}'")
            
            # Step 1: Update field mappings from live APIs
            self._update_field_mappings()
            
            # Step 2: Generate filter payload using intelligent agents
            filter_payload = self._generate_intelligent_filter(user_prompt)
            
            # Step 3: Determine best endpoint
            endpoint = self._determine_endpoint(user_prompt, filter_payload)
            
            # Step 4: Execute API call
            api_response = self._execute_api_call(endpoint, filter_payload)
            
            # Step 5: Format response
            return self._format_response(api_response, endpoint, filter_payload, user_prompt)
            
        except Exception as e:
            print(f"❌ Error processing request: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_prompt": user_prompt,
                "timestamp": datetime.now().isoformat()
            }

    def _update_field_mappings(self):
        """Update field mappings from live APIs with caching"""
        current_time = datetime.now()
        
        # Check cache validity
        if (self.cache_timestamp and 
            (current_time - self.cache_timestamp).seconds < self.cache_duration):
            print("📋 Using cached field mappings")
            return
        
        print("🔄 Fetching fresh field mappings from APIs...")
        
        try:
            mappings = {}
            
            # Fetch priority mappings
            mappings['priority'] = self._fetch_priority_mapping()
            
            # Fetch status mappings
            mappings['status'] = self._fetch_status_mapping()
            
            # Fetch user mappings
            mappings['users'] = self._fetch_user_mapping()
            
            # Fetch location mappings
            mappings['locations'] = self._fetch_location_mapping()
            
            # Fetch category mappings
            mappings['categories'] = self._fetch_category_mapping()
            
            # Update both agents with fresh mappings
            self.llm_agent.update_field_mappings(mappings)
            self.local_agent.update_field_mappings(mappings)
            
            # Update cache
            self.mappings_cache = mappings
            self.cache_timestamp = current_time
            
            print(f"✅ Updated mappings: {list(mappings.keys())}")
            
        except Exception as e:
            print(f"⚠️ Failed to update mappings: {e}")
            # Use cached mappings if available
            if self.mappings_cache:
                self.llm_agent.update_field_mappings(self.mappings_cache)
                self.local_agent.update_field_mappings(self.mappings_cache)

    def _generate_intelligent_filter(self, user_prompt: str) -> Dict[str, Any]:
        """Generate filter using intelligent agents with fallback strategy"""
        try:
            # Try LLM agent first (if available)
            if self.llm_agent:
                try:
                    if self.llm_type == "llama":
                        print("🦙 Trying Llama 3.2 agent...")
                        # Update field mappings for Llama agent
                        if self.mappings_cache:
                            self.llm_agent.update_field_mappings(self.mappings_cache)
                    elif self.llm_type == "openai":
                        print("🤖 Trying OpenAI GPT-4 agent...")

                    llm_payload = self.llm_agent.generate_filter_payload(user_prompt)
                    # Check if we have a valid qualDetails structure (quals can be empty for "all requests")
                    if llm_payload.get('qualDetails') and 'quals' in llm_payload.get('qualDetails', {}):
                        print(f"✅ {self.llm_type.upper()} LLM agent succeeded")
                        return llm_payload
                except Exception as e:
                    print(f"❌ CRITICAL: {self.llm_type.upper()} LLM agent failed: {e}")
                    # In Llama-only mode, always raise error - no fallbacks
                    raise Exception(f"🦙 LLAMA-ONLY MODE: Llama failed - {e}")

            # In Llama-only mode, if we reach here, Llama failed
            if self.llama_only_mode:
                raise Exception("🦙 LLAMA-ONLY MODE: No Llama agent available")

            # Fall back to local intelligence agent (only if not llama-only)
            print("🧠 Using Local Intelligence agent...")
            local_payload = self.local_agent.generate_filter_payload(user_prompt)
            print("✅ Local Intelligence agent succeeded")
            return local_payload

        except Exception as e:
            # In Llama-only mode, propagate the error
            if self.llama_only_mode:
                raise e

            print(f"❌ All intelligent agents failed: {e}")
            return {"qualDetails": {"quals": [], "type": "FlatQualificationRest"}}

    def _fetch_priority_mapping(self) -> Dict[str, int]:
        """Fetch priority mappings from API with re-authentication"""
        max_retries = 2

        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/api/request/priority/search/byqual"
                headers = self._get_auth_headers()

                response = requests.post(url, headers=headers, json={}, verify=False)

                # Check for 401 Unauthorized
                if response.status_code == 401:
                    print(f"🔐 401 Unauthorized in priority mapping (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print("🔄 Re-authenticating and retrying...")
                        self._clear_auth_cache()
                        continue

                response.raise_for_status()
                data = response.json()
                mapping = {}

                for item in data.get('objectList', []):
                    name = item.get('name', '').lower().strip()
                    priority_id = item.get('id')
                    if name and priority_id:
                        mapping[name] = priority_id

                print(f"📊 Priority mapping: {mapping}")
                return mapping

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < max_retries - 1:
                    print(f"🔐 HTTP 401 error in priority mapping (attempt {attempt + 1}/{max_retries})")
                    print("🔄 Re-authenticating and retrying...")
                    self._clear_auth_cache()
                    continue
                else:
                    print(f"❌ Failed to fetch priority mapping: {e}")
                    break
            except Exception as e:
                print(f"❌ Failed to fetch priority mapping: {e}")
                break

        return {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}  # Fallback

    def _fetch_status_mapping(self) -> Dict[str, int]:
        """Fetch status mappings from API with re-authentication"""
        max_retries = 2

        for attempt in range(max_retries):
            try:
                url = f"{self.config.base_url}/api/request/status/search/byqual"
                headers = self.config.get_headers()

                response = requests.post(url, headers=headers, json={}, verify=False)

                # Check for 401 Unauthorized
                if response.status_code == 401:
                    print(f"🔐 401 Unauthorized in status mapping (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print("🔄 Re-authenticating and retrying...")
                        self.config.auth_token = None
                        self._clear_auth_cache()
                        continue

                response.raise_for_status()
                data = response.json()
                mapping = {}

                for item in data.get('objectList', []):
                    name = item.get('name', '').lower().strip()
                    status_id = item.get('id')
                    if name and status_id:
                        mapping[name] = status_id

                print(f"📊 Status mapping: {mapping}")
                return mapping

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < max_retries - 1:
                    print(f"🔐 HTTP 401 error in status mapping (attempt {attempt + 1}/{max_retries})")
                    print("🔄 Re-authenticating and retrying...")
                    self.config.auth_token = None
                    self._clear_auth_cache()
                    continue
                else:
                    print(f"❌ Failed to fetch status mapping: {e}")
                    break
            except Exception as e:
                print(f"❌ Failed to fetch status mapping: {e}")
                break

        return {'open': 9, 'in progress': 10, 'pending': 11, 'closed': 13}  # Fallback

    def _fetch_user_mapping(self) -> Dict[str, int]:
        """Fetch user mappings from API with re-authentication"""
        max_retries = 2

        for attempt in range(max_retries):
            try:
                url = f"{self.config.base_url}/api/request/technician/search/byqual"
                headers = self.config.get_headers()

                response = requests.post(url, headers=headers, json={}, verify=False)

                # Check for 401 Unauthorized
                if response.status_code == 401:
                    print(f"🔐 401 Unauthorized in user mapping (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print("🔄 Re-authenticating and retrying...")
                        self.config.auth_token = None
                        self._clear_auth_cache()
                        continue

                response.raise_for_status()
                data = response.json()
                mapping = {}

                for item in data.get('objectList', []):
                    name = item.get('name', '').lower().strip()
                    user_id = item.get('id')
                    if name and user_id:
                        mapping[name] = user_id

                print(f"📊 User mapping: {dict(list(mapping.items())[:5])}...")
                return mapping

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < max_retries - 1:
                    print(f"🔐 HTTP 401 error in user mapping (attempt {attempt + 1}/{max_retries})")
                    print("🔄 Re-authenticating and retrying...")
                    self.config.auth_token = None
                    self._clear_auth_cache()
                    continue
                else:
                    print(f"❌ Failed to fetch user mapping: {e}")
                    break
            except Exception as e:
                print(f"❌ Failed to fetch user mapping: {e}")
                break

        return {}  # Fallback

    def _fetch_location_mapping(self) -> Dict[str, int]:
        """Fetch location mappings from API"""
        try:
            # This would be implemented based on your location API
            # For now, return sample data
            return {
                'new york': 10, 'london': 15, 'tokyo': 20, 
                'sydney': 25, 'berlin': 30
            }
        except Exception as e:
            print(f"❌ Failed to fetch location mapping: {e}")
            return {}

    def _fetch_category_mapping(self) -> Dict[str, int]:
        """Fetch category mappings from API with re-authentication"""
        max_retries = 2

        for attempt in range(max_retries):
            try:
                url = f"{self.config.base_url}/api/request/category"
                headers = self.config.get_headers()

                response = requests.get(url, headers=headers, verify=False)

                # Check for 401 Unauthorized
                if response.status_code == 401:
                    print(f"🔐 401 Unauthorized in category mapping (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print("🔄 Re-authenticating and retrying...")
                        self.config.auth_token = None
                        self._clear_auth_cache()
                        continue

                response.raise_for_status()
                data = response.json()
                mapping = {}

                # Handle different response formats
                if isinstance(data, list):
                    categories = data
                elif isinstance(data, dict):
                    if 'objectList' in data:
                        categories = data['objectList']
                    elif 'content' in data:
                        categories = data['content']
                    else:
                        categories = [data]
                else:
                    categories = []

                for item in categories:
                    if isinstance(item, dict) and 'name' in item and 'id' in item:
                        name = item.get('name', '').lower().strip()
                        category_id = item.get('id')
                        if name and category_id:
                            mapping[name] = category_id

                print(f"📂 Category mapping: {mapping}")
                return mapping

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < max_retries - 1:
                    print(f"🔐 HTTP 401 error in category mapping (attempt {attempt + 1}/{max_retries})")
                    print("🔄 Re-authenticating and retrying...")
                    self.config.auth_token = None
                    self._clear_auth_cache()
                    continue
                else:
                    print(f"❌ Failed to fetch category mapping: {e}")
                    break
            except Exception as e:
                print(f"❌ Failed to fetch category mapping: {e}")
                break

        return {'it': 5, 'hr': 7, 'facilities': 9, 'finance': 11, 'security': 13}  # Fallback

    def _determine_endpoint(self, user_prompt: str, filter_payload: Dict) -> str:
        """Determine the best endpoint based on request"""
        # For now, default to requests endpoint
        # This could be enhanced with LLM-based endpoint selection
        return "requests"

    def _execute_api_call(self, endpoint: str, filter_payload: Dict) -> Dict:
        """Execute the API call with generated filter and auto re-authentication"""
        max_retries = 2

        for attempt in range(max_retries):
            try:
                if endpoint == "requests":
                    # Add required query parameters - increased size to get all records
                    url = f"{self.config.base_url}/api/request/search/byqual?offset=0&size=200&sort_by=createdTime"
                else:
                    raise ValueError(f"Unknown endpoint: {endpoint}")

                headers = self.config.get_headers()

                print(f"🌐 Calling API: {url}")
                print(f"📋 Filter payload: {json.dumps(filter_payload, indent=2)}")

                response = requests.post(url, headers=headers, json=filter_payload, verify=False)

                # Check for 401 Unauthorized
                if response.status_code == 401:
                    print(f"🔐 401 Unauthorized detected (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print("🔄 Re-authenticating and retrying...")
                        # Clear current token and force re-authentication
                        self.config.auth_token = None
                        self._clear_auth_cache()
                        continue
                    else:
                        print("❌ Re-authentication failed after maximum retries")

                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < max_retries - 1:
                    print(f"🔐 HTTP 401 error detected (attempt {attempt + 1}/{max_retries})")
                    print("🔄 Re-authenticating and retrying...")
                    # Clear current token and force re-authentication
                    self.config.auth_token = None
                    self._clear_auth_cache()
                    continue
                else:
                    print(f"❌ API call failed: {e}")
                    raise
            except Exception as e:
                print(f"❌ API call failed: {e}")
                raise

        # If we get here, all retries failed
        raise Exception("API call failed after all retry attempts")

    def _clear_auth_cache(self):
        """Clear authentication cache to force re-authentication"""
        self.auth_token = None
        if hasattr(self, 'config') and hasattr(self.config, 'auth_token'):
            self.config.auth_token = None
        print("🔄 Authentication cache cleared")

    def _format_response(self, api_response: Dict, endpoint: str,
                        filter_payload: Dict, user_prompt: str) -> Dict:
        """Format the final response"""
        return {
            "success": True,
            "data": api_response.get('objectList', []),
            "total_count": len(api_response.get('objectList', [])),
            "endpoint_used": endpoint,
            "qualification": filter_payload,
            "user_prompt": user_prompt,
            "timestamp": datetime.now().isoformat(),
            "llm_powered": True
        }

    def test_llm_understanding(self, test_prompts: List[str]) -> Dict:
        """Test LLM understanding with various prompts"""
        results = {}
        
        print("🧪 Testing LLM Understanding:")
        print("=" * 50)
        
        for prompt in test_prompts:
            try:
                # Update mappings
                self._update_field_mappings()
                
                # Generate filter
                filter_payload = self.llm_agent.generate_filter_payload(prompt)
                
                results[prompt] = {
                    "success": True,
                    "filter": filter_payload,
                    "quals_count": len(filter_payload.get('qualDetails', {}).get('quals', []))
                }
                
                print(f"✅ '{prompt}' → {results[prompt]['quals_count']} filters")
                
            except Exception as e:
                results[prompt] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ '{prompt}' → Error: {e}")
        
        return results

    def _get_auth_headers(self):
        """Get authentication headers for API requests"""
        if not self.auth_token:
            self._get_access_token()

        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    def _get_access_token(self):
        """Get access token for API authentication"""
        import requests

        # Use correct OAuth endpoint
        token_url = "http://172.16.15.113/api/oauth/token"

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Authorization': 'Basic ZmxvdG8td2ViLWFwcDpjN3ByZE5KRVdFQmt4NGw3ZmV6bA==',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'http://172.16.15.113',
            'Referer': 'http://172.16.15.113/login?redirectFrom=%2Ft%2Frequest%2F',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }

        # Use URL-encoded format as shown in curl
        data = 'username=automind%40motadata.com&password=2d7QdRn6bMI1Q2vQBhficw%3D%3D&grant_type=password'

        try:
            response = requests.post(token_url, headers=headers, data=data, verify=False)
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                print("✅ Token obtained successfully")
            else:
                print(f"❌ Token request failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Token request error: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize enhanced agent
    agent = EnhancedMultiEndpointAgent()
    
    # Test prompts covering various scenarios
    test_prompts = [
        # Simple filters
        "Show high priority tickets",
        "Find open tickets",
        "Get tickets created today",
        
        # Complex combinations
        "Show high priority open tickets from last week",
        "Find critical issues assigned to John",
        "Get tickets not closed with medium priority",
        
        # Natural language variations
        "What tickets need my attention?",
        "Show me urgent stuff from yesterday",
        "Find tickets that are stuck",
        
        # Edge cases
        "Display tickets with no assignee",
        "Show tickets containing login in subject",
        "Find tickets older than 30 days"
    ]
    
    # Test LLM understanding
    results = agent.test_llm_understanding(test_prompts)
    
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    # Test actual execution with a simple prompt
    print("\n🎯 Testing Actual Execution:")
    print("=" * 50)
    
    try:
        result = agent.execute_request("Show high priority open tickets")
        print(f"✅ Execution successful!")
        print(f"📊 Found {result.get('total_count', 0)} tickets")
        print(f"🔧 Used {len(result.get('qualification', {}).get('qualDetails', {}).get('quals', []))} filters")
    except Exception as e:
        print(f"❌ Execution failed: {e}")
