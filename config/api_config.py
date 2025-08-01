#!/usr/bin/env python3
"""
API Configuration
=================

Configuration settings for the API Request Agent.
"""

import os

class APIConfig:
    """API configuration settings"""
    
    # API Base Configuration
    BASE_URL = "https://172.16.15.113"
    OAUTH_URL = f"{BASE_URL}/api/oauth/token"
    REQUEST_SEARCH_URL = f"{BASE_URL}/api/request/search/byqual"
    STATUS_SEARCH_URL = f"{BASE_URL}/api/request/status/search/byqual"
    
    # OAuth Credentials
    USERNAME = "automind@motadata.com"
    PASSWORD = "2d7QdRn6bMI1Q2vQBhficw=="
    CLIENT_AUTH = "Basic ZmxvdG8td2ViLWFwcDpjN3ByZE5KRVdFQmt4NGw3ZmV6bA=="
    
    # Default Request Parameters
    DEFAULT_OFFSET = 0
    DEFAULT_SIZE = 25
    DEFAULT_SORT_BY = "createdTime"
    
    # Priority Mappings
    PRIORITY_MAPPING = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "urgent": 4
    }
    
    # Status Configuration
    CLOSED_STATUS_ID = 13  # Status ID for closed requests (excluded by default)
    
    # Server Configuration
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5000
    DEBUG_MODE = True
    
    # Timeouts
    REQUEST_TIMEOUT = 30
    TOKEN_REFRESH_BUFFER = 60  # Refresh token 60 seconds before expiry
    
    # Database
    KNOWLEDGE_DB_NAME = "knowledge.db"
    
    @classmethod
    def get_priority_id(cls, priority_name):
        """Get priority ID from name"""
        return cls.PRIORITY_MAPPING.get(priority_name.lower())
    
    @classmethod
    def get_priority_name(cls, priority_id):
        """Get priority name from ID"""
        for name, pid in cls.PRIORITY_MAPPING.items():
            if pid == priority_id:
                return name.title()
        return "Unknown"
    
    @classmethod
    def get_all_priority_ids(cls):
        """Get all priority IDs"""
        return list(cls.PRIORITY_MAPPING.values())
    
    @classmethod
    def validate_config(cls):
        """Validate configuration"""
        required_fields = [
            'BASE_URL', 'USERNAME', 'PASSWORD', 'CLIENT_AUTH'
        ]
        
        for field in required_fields:
            if not getattr(cls, field, None):
                raise ValueError(f"Missing required configuration: {field}")
        
        return True

# Environment-based overrides
if os.getenv('API_BASE_URL'):
    APIConfig.BASE_URL = os.getenv('API_BASE_URL')
    APIConfig.OAUTH_URL = f"{APIConfig.BASE_URL}/api/oauth/token"
    APIConfig.REQUEST_SEARCH_URL = f"{APIConfig.BASE_URL}/api/request/search/byqual"

if os.getenv('API_USERNAME'):
    APIConfig.USERNAME = os.getenv('API_USERNAME')

if os.getenv('API_PASSWORD'):
    APIConfig.PASSWORD = os.getenv('API_PASSWORD')

if os.getenv('SERVER_PORT'):
    APIConfig.SERVER_PORT = int(os.getenv('SERVER_PORT'))

if os.getenv('DEBUG_MODE'):
    APIConfig.DEBUG_MODE = os.getenv('DEBUG_MODE').lower() == 'true'
