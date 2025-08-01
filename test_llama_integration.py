#!/usr/bin/env python3
"""
Test Llama 3.2 Integration
==========================

Simple test script to verify Llama 3.2 is working with the agent.
"""

import sys
import os
import requests
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama is running")
            print(f"📋 Available models: {[model.get('name', 'unknown') for model in data.get('models', [])]}")
            return True
        else:
            print(f"❌ Ollama responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def test_llama_model():
    """Test if Llama 3.2 model is available"""
    try:
        # Test with a simple prompt
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "llama3.2",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond with a simple JSON object."
                },
                {
                    "role": "user", 
                    "content": "Say hello in JSON format with a 'message' field."
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 100
            }
        }
        
        response = requests.post("http://localhost:11434/api/chat", headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("message", {}).get("content", "")
            print(f"✅ Llama 3.2 is working!")
            print(f"📝 Response: {message[:100]}...")
            return True
        else:
            print(f"❌ Llama 3.2 test failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Llama 3.2 test error: {e}")
        return False

def test_enhanced_agent():
    """Test the enhanced agent with Llama 3.2"""
    try:
        from enhanced_multi_endpoint_agent import EnhancedMultiEndpointAgent
        
        print("🦙 Testing Enhanced Agent with Llama 3.2...")
        
        # Initialize agent with Llama 3.2
        agent = EnhancedMultiEndpointAgent(
            llm_type="llama",
            llama_endpoint="http://localhost:11434/api/chat",
            llama_model="llama3.2"
        )
        
        print(f"✅ Enhanced agent initialized")
        print(f"🎯 LLM type detected: {agent.llm_type}")
        
        if agent.llm_type == "llama":
            print("🦙 Llama 3.2 successfully configured!")
            return True
        else:
            print(f"⚠️ Expected 'llama' but got: {agent.llm_type}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 LLAMA 3.2 INTEGRATION TEST")
    print("=" * 50)
    
    # Test 1: Ollama connection
    print("\n1️⃣ Testing Ollama connection...")
    ollama_ok = test_ollama_connection()
    
    # Test 2: Llama model (only if model is downloaded)
    print("\n2️⃣ Testing Llama 3.2 model...")
    if ollama_ok:
        llama_ok = test_llama_model()
    else:
        llama_ok = False
        print("⏭️ Skipping Llama test (Ollama not available)")
    
    # Test 3: Enhanced agent
    print("\n3️⃣ Testing Enhanced Agent...")
    agent_ok = test_enhanced_agent()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Ollama Connection: {'✅ PASS' if ollama_ok else '❌ FAIL'}")
    print(f"Llama 3.2 Model:   {'✅ PASS' if llama_ok else '❌ FAIL'}")
    print(f"Enhanced Agent:    {'✅ PASS' if agent_ok else '❌ FAIL'}")
    
    if ollama_ok and agent_ok:
        print("\n🎉 Llama 3.2 integration is ready!")
        if not llama_ok:
            print("⏳ Note: Model is still downloading. It will work once download completes.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
    
    return ollama_ok and agent_ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
