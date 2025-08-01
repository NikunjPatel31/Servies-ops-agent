#!/usr/bin/env python3
"""
API Request Agent - Main Entry Point
====================================

Main entry point for the API Request Agent system.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api_endpoint_server import app, executor
from config.api_config import APIConfig

def main():
    """Main entry point"""
    print("🚀 API REQUEST AGENT")
    print("=" * 50)
    print("Natural Language to API Execution System")
    print("=" * 50)
    
    # Validate configuration
    try:
        APIConfig.validate_config()
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Show configuration
    print(f"🔗 API Base URL: {APIConfig.BASE_URL}")
    print(f"👤 Username: {APIConfig.USERNAME}")
    print(f"🌐 Server: http://{APIConfig.SERVER_HOST}:{APIConfig.SERVER_PORT}")
    print(f"🎯 Priority Mapping: {APIConfig.PRIORITY_MAPPING}")
    
    print("\n📡 Starting API endpoint server...")
    print("📋 Endpoint: POST /execute-request")
    print("📚 Example: {\"request\": \"Get all the request with priority as low\"}")
    print("🔗 Health check: GET /health")
    print("📖 Examples: GET /examples")
    print("=" * 50)
    
    try:
        # Start the Flask server
        app.run(
            host=APIConfig.SERVER_HOST,
            port=APIConfig.SERVER_PORT,
            debug=APIConfig.DEBUG_MODE
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
