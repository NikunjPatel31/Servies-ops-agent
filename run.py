#!/usr/bin/env python3
"""
Quick Start Script
==================

Simple script to run the API Request Agent server.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

from api_endpoint_server import app
from api_config import APIConfig

if __name__ == '__main__':
    print("🚀 API REQUEST AGENT - Quick Start")
    print("=" * 40)
    print(f"🌐 Server: http://localhost:{APIConfig.SERVER_PORT}")
    print(f"📡 Endpoint: POST /execute-request")
    print("=" * 40)
    
    app.run(
        host=APIConfig.SERVER_HOST,
        port=APIConfig.SERVER_PORT,
        debug=APIConfig.DEBUG_MODE
    )
