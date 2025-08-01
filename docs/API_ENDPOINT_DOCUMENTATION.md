# 🎯 API Endpoint Documentation

## Overview

This endpoint takes natural language prompts from users, generates the appropriate API calls, executes them, and returns the results. It's specifically trained on your request search API with priority filtering.

## 🚀 Quick Start

### Start the Server
```bash
source venv/bin/activate
python3 api_endpoint_server.py
```

### Test the Endpoint
```bash
curl -X POST http://localhost:5000/execute-request \
  -H "Content-Type: application/json" \
  -d '{"request": "Get all the request with priority as low"}'
```

## 📡 API Endpoints

### POST /execute-request

**Purpose**: Execute API calls based on natural language prompts

**Request Body**:
```json
{
  "request": "Get all the request with priority as low",
  "token": "optional-custom-bearer-token"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "data": { /* actual API response data */ },
  "api_call": {
    "url": "http://172.16.15.113/api/request/search/byqual?offset=0&size=25&sort_by=createdTime",
    "method": "POST",
    "request_body": { /* qualification filters */ },
    "priority_filter": [1],
    "parameters": {"offset": 0, "size": 25, "sort_by": "createdTime"}
  },
  "message": "Found X requests",
  "user_prompt": "Get all the request with priority as low",
  "timestamp": "2025-08-01T..."
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": "API call failed with status 401",
  "details": "Session has timed out",
  "api_call": { /* generated API call details */ },
  "user_prompt": "Get all the request with priority as low",
  "timestamp": "2025-08-01T..."
}
```

### GET /health

**Purpose**: Health check

**Response**:
```json
{
  "status": "healthy",
  "service": "API Endpoint Server",
  "timestamp": "2025-08-01T..."
}
```

### GET /examples

**Purpose**: Get example requests

**Response**:
```json
{
  "examples": [
    {
      "description": "Get low priority requests",
      "request": {"request": "Get all the request with priority as low"}
    }
  ],
  "endpoint": "/execute-request",
  "method": "POST"
}
```

## 🎯 Supported Prompts

### Priority-Based Queries

| User Prompt | Priority IDs | Description |
|-------------|--------------|-------------|
| "Get all the request with priority as low" | [1] | Low priority only |
| "Show me medium priority requests" | [2] | Medium priority only |
| "Find high priority requests" | [3] | High priority only |
| "Get urgent priority requests" | [4] | Urgent priority only |
| "Show me low and medium requests" | [1, 2] | Low + Medium |
| "Find high and urgent requests" | [3, 4] | High + Urgent |
| "Get all active requests" | [] | All priorities |

### Priority Mapping

- **Priority ID 1** = Low priority
- **Priority ID 2** = Medium priority  
- **Priority ID 3** = High priority
- **Priority ID 4** = Urgent priority

## 🔧 How It Works

1. **Parse Prompt**: Analyzes natural language to extract intent
2. **Generate API Call**: Creates appropriate qualification filters
3. **Execute Request**: Makes HTTP call to your API
4. **Return Results**: Provides structured response with data

## 🛠️ Generated API Structure

The endpoint automatically generates this API call structure:

```json
{
  "qualDetails": {
    "type": "FlatQualificationRest",
    "quals": [
      {
        "type": "RelationalQualificationRest",
        "leftOperand": {"type": "PropertyOperandRest", "key": "request.statusId"},
        "operator": "not_in",
        "rightOperand": {"type": "ValueOperandRest", "value": {"type": "ListLongValueRest", "value": [13]}}
      },
      {
        "type": "RelationalQualificationRest",
        "leftOperand": {"type": "PropertyOperandRest", "key": "request.priorityId"},
        "operator": "in",
        "rightOperand": {"type": "ValueOperandRest", "value": {"type": "ListLongValueRest", "value": [1]}}
      }
    ]
  }
}
```

## 🧪 Testing

### Run All Tests
```bash
python3 test_api_endpoint.py
```

### Interactive Testing
```bash
python3 test_api_endpoint.py interactive
```

### cURL Testing
```bash
./test_curl_endpoint.sh
```

### Demo
```bash
python3 demo_endpoint.py
```

## 🔐 Authentication

- Uses Bearer token authentication
- Default token included (may be expired)
- Pass custom token in request body: `{"request": "...", "token": "your-token"}`

## 📊 Features

✅ **Natural Language Processing**: Understands priority-based queries  
✅ **Smart Filtering**: Always excludes closed requests (status ID 13)  
✅ **Flexible Priorities**: Supports single or multiple priority combinations  
✅ **Pagination**: Configurable offset, size, and sorting  
✅ **Error Handling**: Comprehensive error responses  
✅ **Structured Output**: Detailed API call information  
✅ **Health Monitoring**: Health check endpoint  

## 🚀 Production Deployment

For production use:

1. **Update Configuration**: Set correct API host and default token
2. **Use WSGI Server**: Replace Flask dev server with Gunicorn/uWSGI
3. **Add Security**: Implement rate limiting, input validation
4. **Enable HTTPS**: Use SSL certificates
5. **Add Logging**: Comprehensive request/response logging

## 📝 Example Usage

```python
import requests

# Your exact use case
response = requests.post('http://localhost:5000/execute-request', json={
    "request": "Get all the request with priority as low"
})

data = response.json()
if data['success']:
    requests_found = data['data']
    print(f"Found {len(requests_found)} low priority requests")
else:
    print(f"Error: {data['error']}")
```

## 🎉 Success!

Your endpoint is now ready to:
- ✅ Accept natural language prompts
- ✅ Generate correct API calls  
- ✅ Execute HTTP requests
- ✅ Return structured results

**Perfect for your use case**: *"Get all the request with priority as low"* → **Complete API execution with results!**
