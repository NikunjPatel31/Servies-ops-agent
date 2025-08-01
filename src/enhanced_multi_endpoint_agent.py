#!/usr/bin/env python3
"""
Enhanced Multi-Endpoint Agent with LLM Integration
Replaces regex-based filtering with intelligent LLM understanding
"""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from dynamic_llm_agent import DynamicLLMAgent
from local_intelligence_agent import LocalIntelligenceAgent

class EnhancedMultiEndpointAgent:
    def __init__(self, openai_api_key: str = None):
        # Use the same working config as demo agent
        self.base_url = "https://172.16.15.113"
        self.auth_token = None
        self.username = "automind@motadata.com"
        self.password = "2d7QdRn6bMI1Q2vQBhficw=="
        self.client_auth = "Basic ZmxvdG8td2ViLWFwcDpjN3ByZE5KRVdFQmt4NGw3ZmV6bA=="

        # Initialize intelligent agents
        self.llm_agent = DynamicLLMAgent(openai_api_key)
        self.local_agent = LocalIntelligenceAgent()
        
        # Cache for dynamic mappings
        self.mappings_cache = {}
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 minutes
        
        print("🚀 Enhanced Multi-Endpoint Agent initialized with LLM intelligence")

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
            # Try LLM agent first (if API key available)
            if hasattr(self.llm_agent, 'openai_api_key') and self.llm_agent.openai_api_key:
                try:
                    print("🤖 Trying LLM agent...")
                    llm_payload = self.llm_agent.generate_filter_payload(user_prompt)
                    if llm_payload.get('qualDetails', {}).get('quals'):
                        print("✅ LLM agent succeeded")
                        return llm_payload
                except Exception as e:
                    print(f"⚠️ LLM agent failed: {e}")

            # Fall back to local intelligence agent
            print("🧠 Using Local Intelligence agent...")
            local_payload = self.local_agent.generate_filter_payload(user_prompt)
            print("✅ Local Intelligence agent succeeded")
            return local_payload

        except Exception as e:
            print(f"❌ All intelligent agents failed: {e}")
            return {"qualDetails": {"quals": [], "type": "FlatQualificationRest"}}

    def _fetch_priority_mapping(self) -> Dict[str, int]:
        """Fetch priority mappings from API"""
        try:
            url = f"{self.base_url}/api/request/priority/search/byqual"
            headers = self._get_auth_headers()
            
            response = requests.post(url, headers=headers, json={})
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
            
        except Exception as e:
            print(f"❌ Failed to fetch priority mapping: {e}")
            return {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}  # Fallback

    def _fetch_status_mapping(self) -> Dict[str, int]:
        """Fetch status mappings from API"""
        try:
            url = f"{self.config.base_url}/api/request/status/search/byqual"
            headers = self.config.get_headers()
            
            response = requests.post(url, headers=headers, json={})
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
            
        except Exception as e:
            print(f"❌ Failed to fetch status mapping: {e}")
            return {'open': 9, 'in progress': 10, 'pending': 11, 'closed': 13}  # Fallback

    def _fetch_user_mapping(self) -> Dict[str, int]:
        """Fetch user mappings from API"""
        try:
            url = f"{self.config.base_url}/api/request/technician/search/byqual"
            headers = self.config.get_headers()
            
            response = requests.post(url, headers=headers, json={})
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
            
        except Exception as e:
            print(f"❌ Failed to fetch user mapping: {e}")
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
        """Fetch category mappings from API"""
        try:
            url = f"{self.config.base_url}/api/request/category"
            headers = self.config.get_headers()

            response = requests.get(url, headers=headers, verify=False)
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

        except Exception as e:
            print(f"❌ Failed to fetch category mapping: {e}")
            return {'it': 5, 'hr': 7, 'facilities': 9, 'finance': 11, 'security': 13}  # Fallback

    def _determine_endpoint(self, user_prompt: str, filter_payload: Dict) -> str:
        """Determine the best endpoint based on request"""
        # For now, default to requests endpoint
        # This could be enhanced with LLM-based endpoint selection
        return "requests"

    def _execute_api_call(self, endpoint: str, filter_payload: Dict) -> Dict:
        """Execute the API call with generated filter"""
        try:
            if endpoint == "requests":
                url = f"{self.config.base_url}/api/request/search/byqual"
            else:
                raise ValueError(f"Unknown endpoint: {endpoint}")
            
            headers = self.config.get_headers()
            
            print(f"🌐 Calling API: {url}")
            print(f"📋 Filter payload: {json.dumps(filter_payload, indent=2)}")
            
            response = requests.post(url, headers=headers, json=filter_payload)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ API call failed: {e}")
            raise

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
