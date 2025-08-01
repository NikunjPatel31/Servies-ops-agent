# 🎯 API Request Agent

A natural language to API execution system that understands user prompts and automatically generates and executes appropriate API calls.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python main.py
```

### 3. Test the API
```bash
curl -X POST http://localhost:5000/execute-request \
  -H "Content-Type: application/json" \
  -d '{"request": "Get all the request with priority as low"}'
```

## 📋 Features

✅ **Natural Language Processing** - Understands priority-based queries  
✅ **Automatic OAuth Authentication** - Handles token retrieval and refresh  
✅ **Smart API Generation** - Creates appropriate qualification filters  
✅ **Real API Execution** - Actually calls your API and returns results  
✅ **Priority Intelligence** - Understands Low/Medium/High/Urgent priorities  
✅ **Error Handling** - Comprehensive error responses  
✅ **Production Ready** - Structured, configurable, and scalable  

## 🎯 Supported Queries

| User Input | Priority Filter | Description |
|------------|----------------|-------------|
| "Get all the request with priority as low" | [1] | Low priority only |
| "Show me medium priority requests" | [2] | Medium priority only |
| "Find high priority requests" | [3] | High priority only |
| "Get urgent priority requests" | [4] | Urgent priority only |
| "Show me low and medium requests" | [1, 2] | Multiple priorities |
| "Find high and urgent requests" | [3, 4] | High + Urgent |
| "Get all active requests" | [] | All priorities |

## 🏗️ Project Structure

```
api-request-agent/
├── src/                          # Source code
│   ├── api_endpoint_server.py    # Main Flask server
│   ├── request_search_api_agent.py # Core knowledge agent
│   ├── knowledge_agent_tutorial.py # Base knowledge system
│   └── clear_agent_data.py       # Data management utility
├── config/                       # Configuration
│   ├── api_config.py            # API settings and mappings
│   └── __init__.py
├── tests/                        # Test files
│   ├── test_oauth_endpoint.py    # OAuth endpoint tests
│   └── __init__.py
├── docs/                         # Documentation
│   └── API_ENDPOINT_DOCUMENTATION.md
├── main.py                       # Main entry point
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## 🔧 Configuration

Edit `config/api_config.py` to customize:

```python
class APIConfig:
    BASE_URL = "http://172.16.15.113"
    USERNAME = "your-username"
    PASSWORD = "your-password"
    
    PRIORITY_MAPPING = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "urgent": 4
    }
```

### Environment Variables

You can also use environment variables:

```bash
export API_BASE_URL="http://your-api-server.com"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"
export SERVER_PORT=8080
export DEBUG_MODE=false
```

## 📡 API Endpoints

### POST /execute-request

Execute API calls based on natural language prompts.

**Request:**
```json
{
  "request": "Get all the request with priority as low"
}
```

**Response:**
```json
{
  "success": true,
  "data": [/* actual API response data */],
  "api_call": {
    "url": "http://172.16.15.113/api/request/search/byqual?...",
    "method": "POST",
    "priority_filter": [1],
    "parameters": {"offset": 0, "size": 25, "sort_by": "createdTime"}
  },
  "message": "Found X requests",
  "user_prompt": "Get all the request with priority as low",
  "timestamp": "2025-08-01T..."
}
```

### GET /health

Health check endpoint.

### GET /examples

Get example requests and usage patterns.

## 🧪 Testing

### Run Tests
```bash
cd tests
python test_oauth_endpoint.py
```

### Manual Testing
```bash
# Test with cURL
curl -X POST http://localhost:5000/execute-request \
  -H "Content-Type: application/json" \
  -d '{"request": "Show me medium priority requests"}'

# Test health check
curl http://localhost:5000/health

# Get examples
curl http://localhost:5000/examples
```

## 🔐 Authentication

The system automatically handles OAuth authentication:

1. **Automatic Token Retrieval** - Gets fresh tokens using OAuth endpoint
2. **Token Caching** - Caches tokens to avoid unnecessary requests
3. **Auto Refresh** - Refreshes tokens before expiry
4. **Error Handling** - Graceful handling of authentication failures

## 🎯 How It Works

1. **Parse Prompt** - Analyzes natural language to extract intent
2. **Generate Filters** - Creates appropriate qualification filters
3. **Authenticate** - Gets fresh OAuth token automatically
4. **Execute API** - Makes HTTP request to your API
5. **Return Results** - Provides structured response with actual data

## 🚀 Production Deployment

For production use:

1. **Update Configuration** - Set production API URLs and credentials
2. **Use WSGI Server** - Replace Flask dev server with Gunicorn
3. **Enable HTTPS** - Use SSL certificates
4. **Add Monitoring** - Implement logging and health checks
5. **Scale Horizontally** - Deploy multiple instances behind load balancer

### Example with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 📚 Documentation

- [API Endpoint Documentation](docs/API_ENDPOINT_DOCUMENTATION.md) - Complete API reference
- [Configuration Guide](config/api_config.py) - Configuration options
- [Testing Guide](tests/) - Testing procedures

## 🎉 Success!

Your API Request Agent is ready to:
- ✅ Accept natural language prompts
- ✅ Generate correct API calls
- ✅ Handle authentication automatically
- ✅ Execute real API requests
- ✅ Return structured results

**Perfect for converting user requests into API executions!** 🚀
