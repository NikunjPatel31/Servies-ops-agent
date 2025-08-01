#!/usr/bin/env python3
"""
Example Usage
=============

Example of how to use the API Request Agent.
"""

import requests
import json

def test_api_endpoint():
    """Test the API endpoint with example requests"""
    
    base_url = "http://localhost:5000"
    
    # Example requests
    test_requests = [
        "Get all the request with priority as low",
        "Show me medium priority requests",
        "Find high and urgent priority requests",
        "Get all active requests"
    ]
    
    print("🧪 API REQUEST AGENT - EXAMPLE USAGE")
    print("=" * 50)
    
    for i, prompt in enumerate(test_requests, 1):
        print(f"\n{i}. Testing: '{prompt}'")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/execute-request",
                json={"request": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('message', 'API call completed')}")
                
                if 'api_call' in data:
                    api_call = data['api_call']
                    print(f"🎯 Priority Filter: {api_call.get('priority_filter', 'None')}")
                    print(f"📊 Parameters: {api_call.get('parameters', {})}")
                
                if data.get('success') and 'data' in data:
                    api_data = data['data']
                    if isinstance(api_data, dict) and 'totalCount' in api_data:
                        print(f"📋 Found: {api_data['totalCount']} requests")
                    elif isinstance(api_data, list):
                        print(f"📋 Found: {len(api_data)} requests")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - Is the server running?")
            print("   Start with: python run.py")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Example usage complete!")

if __name__ == "__main__":
    test_api_endpoint()
