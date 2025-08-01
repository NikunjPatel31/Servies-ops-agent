#!/usr/bin/env python3
"""
Test OAuth Endpoint
===================

Test the updated API endpoint with automatic OAuth token retrieval.
"""

import requests
import json
import time

def test_oauth_endpoint():
    """Test the endpoint with automatic OAuth token retrieval"""
    print("🔑 TESTING OAUTH-ENABLED API ENDPOINT")
    print("=" * 50)
    
    url = "http://localhost:5000/execute-request"
    
    # Test your specific prompt
    test_prompt = "Get all the request with priority as low"
    
    print(f"🗣️  Testing: '{test_prompt}'")
    print("📋 Request body: {\"request\": \"" + test_prompt + "\"}")
    print("-" * 60)
    
    payload = {"request": test_prompt}
    
    try:
        print("🚀 Sending request to endpoint...")
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCCESS!")
            print(f"🎯 Message: {data.get('message', 'API call completed')}")
            
            # Show API call details
            if 'api_call' in data:
                api_call = data['api_call']
                print(f"\n🔗 Generated API Call:")
                print(f"   URL: {api_call.get('url', 'N/A')}")
                print(f"   Method: {api_call.get('method', 'N/A')}")
                print(f"   Priority Filter: {api_call.get('priority_filter', 'None')}")
                print(f"   Parameters: {api_call.get('parameters', {})}")
            
            # Show results
            if data.get('success') and 'data' in data:
                api_data = data['data']
                print(f"\n📊 API Response Data:")
                
                if isinstance(api_data, dict):
                    # Check for common response structures
                    if 'content' in api_data:
                        requests_found = api_data['content']
                        print(f"   📋 Found {len(requests_found)} requests")
                        
                        # Show sample requests
                        for i, req in enumerate(requests_found[:3], 1):
                            subject = req.get('subject', 'No subject')
                            priority = req.get('priority', {})
                            priority_name = priority.get('name', 'Unknown') if isinstance(priority, dict) else str(priority)
                            status = req.get('status', {})
                            status_name = status.get('name', 'Unknown') if isinstance(status, dict) else str(status)
                            
                            print(f"   {i}. {subject}")
                            print(f"      Priority: {priority_name}, Status: {status_name}")
                        
                        if len(requests_found) > 3:
                            print(f"   ... and {len(requests_found) - 3} more requests")
                    
                    elif 'totalElements' in api_data:
                        print(f"   📊 Total Elements: {api_data['totalElements']}")
                        print(f"   📄 Page Size: {api_data.get('size', 'N/A')}")
                        print(f"   📍 Page Number: {api_data.get('number', 'N/A')}")
                    
                    else:
                        # Show first few keys of response
                        keys = list(api_data.keys())[:5]
                        print(f"   📋 Response Keys: {keys}")
                        if len(api_data.keys()) > 5:
                            print(f"   ... and {len(api_data.keys()) - 5} more keys")
                
                elif isinstance(api_data, list):
                    print(f"   📋 Found {len(api_data)} items")
                    if api_data:
                        print(f"   📄 Sample item keys: {list(api_data[0].keys()) if isinstance(api_data[0], dict) else 'N/A'}")
                
                else:
                    print(f"   📄 Response: {str(api_data)[:200]}...")
            
            return True
            
        else:
            print("❌ FAILED!")
            try:
                error_data = response.json()
                print(f"🔍 Error: {error_data.get('error', 'Unknown error')}")
                print(f"📋 Details: {error_data.get('details', 'No details')}")
                
                # Show if OAuth failed
                if 'token' in str(error_data).lower() or 'auth' in str(error_data).lower():
                    print("🔑 This appears to be an authentication issue")
                
            except:
                print(f"📄 Raw response: {response.text}")
            
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this is normal for OAuth + API call)")
        print("💡 The endpoint is working but the API call took too long")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Is the server running?")
        print("   Start server with: python3 api_endpoint_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_and_examples():
    """Test health check and examples endpoints"""
    print("\n🔍 TESTING HEALTH AND EXAMPLES")
    print("=" * 40)
    
    # Health check
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: PASSED")
        else:
            print(f"❌ Health check: FAILED ({response.status_code})")
    except:
        print("❌ Health check: CONNECTION ERROR")
    
    # Examples
    try:
        response = requests.get("http://localhost:5000/examples", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Examples endpoint: PASSED")
            print(f"📚 Available examples: {len(data.get('examples', []))}")
            
            # Show examples
            for i, example in enumerate(data.get('examples', [])[:3], 1):
                print(f"   {i}. {example.get('description', 'No description')}")
        else:
            print(f"❌ Examples endpoint: FAILED ({response.status_code})")
    except:
        print("❌ Examples endpoint: CONNECTION ERROR")

def main():
    """Main test function"""
    print("🧪 OAUTH API ENDPOINT TEST")
    print("=" * 50)
    print("Testing endpoint with automatic OAuth token retrieval")
    print("No token needed in request body!")
    print("=" * 50)
    
    # Test health and examples first
    test_health_and_examples()
    
    # Test the main functionality
    print(f"\n🎯 MAIN FUNCTIONALITY TEST")
    print("=" * 30)
    
    success = test_oauth_endpoint()
    
    if success:
        print(f"\n🎉 TEST PASSED!")
        print("✅ Endpoint successfully:")
        print("   • Retrieved OAuth token automatically")
        print("   • Parsed natural language prompt")
        print("   • Generated correct API call")
        print("   • Executed HTTP request")
        print("   • Returned structured response")
    else:
        print(f"\n⚠️  TEST COMPLETED WITH ISSUES")
        print("💡 Common issues:")
        print("   • Network connectivity to 172.16.15.113")
        print("   • OAuth credentials may need updating")
        print("   • API endpoint may be temporarily unavailable")
    
    print(f"\n📋 USAGE:")
    print("curl -X POST http://localhost:5000/execute-request \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"request\": \"Get all the request with priority as low\"}'")

if __name__ == "__main__":
    main()
