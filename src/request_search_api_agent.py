#!/usr/bin/env python3
"""
Request Search API Agent
========================

A specialized knowledge agent that understands your request search API.
Trained specifically on the /api/request/search/byqual endpoint.
"""

from knowledge_agent_tutorial import KnowledgeAgent
import json

class RequestSearchAPIAgent:
    """Specialized agent for the request search API"""
    
    def __init__(self, agent_name="RequestSearchExpert"):
        # Clear any existing data first
        self.agent = KnowledgeAgent(agent_name)
        self.agent.knowledge_base.documents = {}
        self.agent.conversation_history = []
        
        # Load the specific API knowledge
        self._load_request_search_api()
        
        print(f"🎯 {agent_name} initialized!")
        print("📚 Specialized in: Request Search API")
    
    def _load_request_search_api(self):
        """Load comprehensive knowledge about the request search API"""
        
        # Main API documentation
        api_doc = """
Request Search API - Get Active Requests
========================================

Endpoint: POST /api/request/search/byqual
Host: 172.16.15.113
Full URL: http://172.16.15.113/api/request/search/byqual

Purpose: Search and retrieve all active requests (excludes closed requests)
Use Case: Display open/active requests in the UI dashboard
Status Filter: Excludes requests with status ID 13 (closed status)

Query Parameters:
• offset: Starting position for pagination (default: 0)
• size: Number of results to return (default: 25, max recommended: 100)
• sort_by: Field to sort results by (createdTime, priority, status, etc.)

Required Headers:
• Authorization: Bearer token authentication required
• Content-Type: application/json
• Accept: application/json, text/plain, */*

Request Body Structure:
{
  "qualDetails": {
    "type": "FlatQualificationRest",
    "quals": [
      {
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "request.statusId"
        },
        "operator": "not_in",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "ListLongValueRest",
            "value": [13]
          }
        }
      }
    ]
  }
}

Response Data:
Returns a paginated list of request objects containing:
• Subject: Request title/description
• Requester: Person who created the request
• Created Date: When the request was submitted
• Assignee: Person assigned to handle the request
• Status: Current status (In Progress, Pending, etc.)
• Priority: Request priority level (Low, Medium, High)
• Due By Status: Deadline information

Authentication:
• Type: Bearer Token (JWT)
• Header: Authorization: Bearer <token>
• Token contains: user info, tenant identifier, expiration
• Tenant: "apolo"

When to Use This API:
• Display active requests dashboard
• Show open tickets to users
• Filter out completed/closed requests
• Paginate through large request lists
• Sort requests by creation time or priority
• Get real-time view of pending work
"""
        
        # Usage examples
        usage_examples = """
Request Search API - Usage Examples
==================================

1. Get First Page of Active Requests:
   GET /api/request/search/byqual?offset=0&size=25&sort_by=createdTime
   
2. Get Next Page (pagination):
   GET /api/request/search/byqual?offset=25&size=25&sort_by=createdTime
   
3. Sort by Priority:
   GET /api/request/search/byqual?offset=0&size=25&sort_by=priority
   
4. Get More Results Per Page:
   GET /api/request/search/byqual?offset=0&size=50&sort_by=createdTime

Common Use Cases:
• Dashboard showing "My Active Requests"
• Admin view of all open tickets
• Request queue for support teams
• Filtering out closed/resolved requests
• Real-time status monitoring

Status ID 13 = Closed/Completed requests (excluded by this API)
All other status IDs = Active requests (included in results)
"""
        
        # Technical details
        technical_details = """
Request Search API - Technical Details
=====================================

HTTP Method: POST (despite being a search operation)
Reason: Complex qualification filters require POST body

Qualification Filter Explanation:
• "not_in" operator excludes specific values
• "request.statusId" targets the status field
• Value [13] means "exclude status ID 13"
• Status ID 13 = Closed/Completed requests

Pagination:
• offset: Skip N records (0-based)
• size: Return N records per page
• Total results available in response metadata

Sorting Options:
• createdTime: Sort by creation date (newest/oldest first)
• priority: Sort by priority level
• status: Sort by current status
• assignee: Sort by assigned person

Response Format:
• JSON array of request objects
• Each request contains all display fields
• Metadata includes total count, pagination info

Performance Notes:
• Recommended page size: 25-50 records
• Large page sizes (>100) may impact performance
• Use pagination for better user experience
• Sort by createdTime for chronological view

Priority Filtering:
• Priority ID 1 = Low priority
• Priority ID 2 = Medium priority
• Priority ID 3 = High priority
• Priority ID 4 = Urgent priority

Priority Filter Examples:
• Low priority only: "key": "request.priorityId", "operator": "in", "value": [1]
• Low + Medium: "key": "request.priorityId", "operator": "in", "value": [1, 2]
• High + Urgent: "key": "request.priorityId", "operator": "in", "value": [3, 4]
• Exclude Low: "key": "request.priorityId", "operator": "not_in", "value": [1]
"""
        
        # Comprehensive ITSM Qualification API Documentation
        itsm_qualification_doc = """
ITSM Qualification-Based Search API - Complete Reference
========================================================

QUALIFICATION TYPES:
===================

1. FlatQualificationRest - Multiple conditions with AND logic
{
  "type": "FlatQualificationRest",
  "quals": [/* Array of QualificationRest objects */]
}

2. RelationalQualificationRest - Compare left operand with right operand
{
  "type": "RelationalQualificationRest",
  "leftOperand": {/* OperandRest */},
  "operator": "Equal",
  "rightOperand": {/* OperandRest */}
}

3. BinaryQualificationRest - Combine two qualifications with AND/OR
{
  "type": "BinaryQualificationRest",
  "leftQual": {/* QualificationRest */},
  "operator": "AND",
  "rightQual": {/* QualificationRest */}
}

4. UnaryQualificationRest - Single operand operations (IS_NULL, etc.)
{
  "type": "UnaryQualificationRest",
  "operand": {/* OperandRest */},
  "operator": "Is_Null"
}

5. BatchQualificationRest - Multiple qualifications with explicit operator
{
  "type": "BatchQualificationRest",
  "quals": [/* Array */],
  "operator": "OR"
}

OPERAND TYPES:
=============

1. PropertyOperandRest - Entity properties
{
  "type": "PropertyOperandRest",
  "key": "request.statusId"
}

Common Property Keys:
• request.statusId - Request status ID
• request.priorityId - Priority ID
• request.urgencyId - Urgency ID
• request.impactId - Impact ID
• request.name - Request name/subject
• request.subject - Request subject
• request.description - Request description
• request.requesterId - Requester ID
• request.technicianId - Assigned technician ID
• request.groupId - Assigned group ID
• request.categoryId - Category ID
• request.createdTime - Creation timestamp
• request.updatedTime - Last update timestamp
• request.dueByTime - Due date timestamp
• request.tags - Request tags

2. ValueOperandRest - Actual values
{
  "type": "ValueOperandRest",
  "value": {/* ValueRest object */}
}

3. CustomFieldOperandRest - Custom fields
{
  "type": "CustomFieldOperandRest",
  "fieldName": "Department"
}

OPERATORS:
=========

Relational Operators:
• Equal - Exact match
• Not_Equal - Not equal
• Like - SQL LIKE pattern
• Contains - String contains
• Not_Contains - String doesn't contain
• Start_With - String starts with
• End_With - String ends with
• In - Value in list
• Not_In - Value not in list
• LessThan - Less than
• LessThanOrEqual - Less than or equal
• GreaterThan - Greater than
• GreaterThanOrEqual - Greater than or equal
• Between - Between two values
• Before - Date before
• After - Date after

Case-Insensitive Variants:
• Equal_Case_Insensitive
• Not_Equal_Case_Insensitive
• In_Case_Insensitive
• Not_In_Case_Insensitive

Member Operations:
• Is_Member - Check if value is member of collection
• All_Members_Exist - All values exist in collection
• Any_Member_Or_All_Members_Exist - Any or all values exist
• No_Members_Exist - No values exist in collection

Unary Operators:
• Is_Null - Field is null
• Is_Not_Null - Field is not null
• IS_EMPTY - Collection is empty
• IS_NOT_EMPTY - Collection is not empty
• IS_BLANK - String is blank/empty
• IS_NOT_BLANK - String is not blank

Binary Operators:
• AND - Logical AND
• OR - Logical OR

VALUE TYPES:
===========

Basic Types:
• StringValueRest - {"type": "StringValueRest", "value": "text"}
• LongValueRest - {"type": "LongValueRest", "value": 123}
• IntegerValueRest - {"type": "IntegerValueRest", "value": 42}
• DoubleValueRest - {"type": "DoubleValueRest", "value": 3.14}
• BooleanValueRest - {"type": "BooleanValueRest", "value": true}
• TimeValueRest - {"type": "TimeValueRest", "value": "2024-01-15T10:30:00Z"}

List Types:
• ListLongValueRest - {"type": "ListLongValueRest", "value": [1, 2, 3]}
• ListStringValueRest - {"type": "ListStringValueRest", "value": ["Open", "Closed"]}
• ListIntegerValueRest - {"type": "ListIntegerValueRest", "value": [1, 2, 3]}

COMMON PATTERNS:
===============

1. Status Filtering (Exclude closed):
{
  "type": "RelationalQualificationRest",
  "leftOperand": {"type": "PropertyOperandRest", "key": "request.statusId"},
  "operator": "Not_In",
  "rightOperand": {"type": "ValueOperandRest", "value": {"type": "ListLongValueRest", "value": [13]}}
}

2. Priority Filtering:
{
  "type": "RelationalQualificationRest",
  "leftOperand": {"type": "PropertyOperandRest", "key": "request.priorityId"},
  "operator": "In",
  "rightOperand": {"type": "ValueOperandRest", "value": {"type": "ListLongValueRest", "value": [1, 2]}}
}

3. Text Search in Subject:
{
  "type": "RelationalQualificationRest",
  "leftOperand": {"type": "PropertyOperandRest", "key": "request.subject"},
  "operator": "Contains",
  "rightOperand": {"type": "ValueOperandRest", "value": {"type": "StringValueRest", "value": "urgent"}}
}

4. Date Range (Last 7 days):
{
  "type": "RelationalQualificationRest",
  "leftOperand": {"type": "PropertyOperandRest", "key": "request.createdTime"},
  "operator": "GreaterThanOrEqual",
  "rightOperand": {"type": "ValueOperandRest", "value": {"type": "TimeValueRest", "value": "2024-01-08T00:00:00Z"}}
}

5. Null Check (Unassigned requests):
{
  "type": "UnaryQualificationRest",
  "operand": {"type": "PropertyOperandRest", "key": "request.technicianId"},
  "operator": "Is_Null"
}

6. Tag Filtering:
{
  "type": "RelationalQualificationRest",
  "leftOperand": {"type": "PropertyOperandRest", "key": "request.tags"},
  "operator": "All_Members_Exist",
  "rightOperand": {"type": "ValueOperandRest", "value": {"type": "ListStringValueRest", "value": ["urgent", "hardware"]}}
}

COMPLEX EXAMPLES:
================

Multiple AND Conditions:
{
  "type": "FlatQualificationRest",
  "quals": [
    {/* Status filter */},
    {/* Priority filter */},
    {/* Date filter */}
  ]
}

OR Logic:
{
  "type": "BinaryQualificationRest",
  "leftQual": {/* High priority */},
  "operator": "OR",
  "rightQual": {/* Contains "critical" */}
}

Mixed Logic (AND + OR):
{
  "type": "BinaryQualificationRest",
  "leftQual": {
    "type": "FlatQualificationRest",
    "quals": [{/* Status */}, {/* Priority */}]
  },
  "operator": "OR",
  "rightQual": {/* Subject contains "critical" */}
}
"""

        # Learn all the documentation
        docs = [
            ("Request Search API - Main Documentation", api_doc),
            ("Request Search API - Usage Examples", usage_examples),
            ("Request Search API - Technical Details", technical_details),
            ("ITSM Qualification API - Complete Reference", itsm_qualification_doc)
        ]
        
        for title, content in docs:
            self.agent.learn_from_text(content, title)
        
        print("✅ Request Search API knowledge loaded!")
    
    def ask_about_api(self, question: str) -> str:
        """Ask questions about the request search API"""
        # Check if user is asking for specific priority requests
        if self._is_priority_request(question):
            return self._generate_priority_api_call(question)

        return self.agent.ask(question)

    def _is_priority_request(self, question: str) -> bool:
        """Check if the question is asking for requests by priority"""
        question_lower = question.lower()
        priority_keywords = ['priority', 'low', 'medium', 'high', 'urgent']
        request_keywords = ['request', 'requests', 'give me', 'get', 'show', 'find']

        has_priority = any(keyword in question_lower for keyword in priority_keywords)
        has_request = any(keyword in question_lower for keyword in request_keywords)

        return has_priority and has_request

    def _generate_priority_api_call(self, question: str) -> str:
        """Generate API call based on priority request"""
        question_lower = question.lower()

        # Determine priority IDs based on question
        priority_ids = []
        if 'low' in question_lower:
            priority_ids.append(1)
        if 'medium' in question_lower:
            priority_ids.append(2)
        if 'high' in question_lower:
            priority_ids.append(3)
        if 'urgent' in question_lower:
            priority_ids.append(4)

        # If no specific priority mentioned, ask for clarification
        if not priority_ids:
            return """
🤔 I need to know which priority level you want:
• Low priority (ID: 1)
• Medium priority (ID: 2)
• High priority (ID: 3)
• Urgent priority (ID: 4)

Please specify like: "give me all low priority requests" or "show me high and urgent requests"
"""

        # Generate the API call
        priority_names = []
        if 1 in priority_ids: priority_names.append("Low")
        if 2 in priority_ids: priority_names.append("Medium")
        if 3 in priority_ids: priority_names.append("High")
        if 4 in priority_ids: priority_names.append("Urgent")

        priority_text = " + ".join(priority_names)

        # Create the qualification filter
        request_body = {
            "qualDetails": {
                "type": "FlatQualificationRest",
                "quals": [
                    {
                        "type": "RelationalQualificationRest",
                        "leftOperand": {
                            "type": "PropertyOperandRest",
                            "key": "request.statusId"
                        },
                        "operator": "not_in",
                        "rightOperand": {
                            "type": "ValueOperandRest",
                            "value": {
                                "type": "ListLongValueRest",
                                "value": [13]
                            }
                        }
                    },
                    {
                        "type": "RelationalQualificationRest",
                        "leftOperand": {
                            "type": "PropertyOperandRest",
                            "key": "request.priorityId"
                        },
                        "operator": "in",
                        "rightOperand": {
                            "type": "ValueOperandRest",
                            "value": {
                                "type": "ListLongValueRest",
                                "value": priority_ids
                            }
                        }
                    }
                ]
            }
        }

        import json

        return f"""
🎯 API CALL FOR {priority_text.upper()} PRIORITY REQUESTS

Endpoint: POST /api/request/search/byqual?offset=0&size=25&sort_by=createdTime
Host: 172.16.15.113

cURL Command:
```bash
curl 'http://172.16.15.113/api/request/search/byqual?offset=0&size=25&sort_by=createdTime' \\
  -H 'Authorization: Bearer <your-token>' \\
  -H 'Content-Type: application/json' \\
  --data-raw '{json.dumps(request_body, separators=(",", ":"))}' \\
  --insecure
```

Request Body (formatted):
```json
{json.dumps(request_body, indent=2)}
```

This will return:
• Active requests (excludes closed status ID 13)
• With {priority_text} priority only
• Paginated results (25 per page)
• Sorted by creation time

Priority IDs used: {priority_ids}
"""
    
    def get_api_usage_guide(self) -> str:
        """Get a quick usage guide for the API"""
        return """
🎯 REQUEST SEARCH API - QUICK GUIDE

Endpoint: POST /api/request/search/byqual
Purpose: Get all active requests (excludes closed ones)

Basic Usage:
curl 'http://172.16.15.113/api/request/search/byqual?offset=0&size=25&sort_by=createdTime' \\
  -H 'Authorization: Bearer <your-token>' \\
  -H 'Content-Type: application/json' \\
  --data-raw '{"qualDetails":{"type":"FlatQualificationRest","quals":[{"type":"RelationalQualificationRest","leftOperand":{"type":"PropertyOperandRest","key":"request.statusId"},"operator":"not_in","rightOperand":{"type":"ValueOperandRest","value":{"type":"ListLongValueRest","value":[13]}}}]}}'

Key Points:
• Excludes status ID 13 (closed requests)
• Returns paginated results
• Requires Bearer token authentication
• Use for dashboard/active request views
"""
    
    def when_to_use_api(self) -> str:
        """Explain when to use this API"""
        return """
🎯 WHEN TO USE REQUEST SEARCH API

Use this API when you need to:

✅ Display Active Requests Dashboard
   - Show open tickets to users
   - Real-time view of pending work
   - Filter out completed requests

✅ Support Team Queue
   - List requests needing attention
   - Prioritize work by creation time
   - Show assigned vs unassigned requests

✅ Management Reporting
   - Count of active requests
   - Workload distribution
   - Performance monitoring

✅ User Self-Service
   - "My Open Requests" view
   - Track request status
   - See pending items

❌ Don't use for:
   - Getting closed/completed requests
   - Historical reporting (includes closed)
   - Specific request details (use single request API)
   - Creating new requests (use create API)
"""
    
    def get_stats(self) -> dict:
        """Get agent statistics"""
        stats = self.agent.get_stats()
        stats['specialization'] = 'Request Search API'
        return stats

def interactive_request_api_expert():
    """Interactive expert for request search API"""
    print("🎯 REQUEST SEARCH API EXPERT")
    print("=" * 40)
    print("I'm specialized in the request search API!")
    print("Ask me anything about getting active requests.")
    print("=" * 40)
    
    expert = RequestSearchAPIAgent()
    
    print("\n✅ Ready! Ask me about the request search API.")
    print("\nExample questions:")
    print("• When should I use this API?")
    print("• How do I get the next page of results?")
    print("• What does the qualification filter do?")
    print("• How do I sort by priority?")
    print("• What authentication is required?")
    print("• What data does the response contain?")
    
    while True:
        try:
            question = input(f"\n🎯 Ask the expert: ").strip()
            
            if not question or question.lower() in ['quit', 'exit']:
                print("👋 Happy coding with your request API!")
                break
            
            if question.lower() == 'guide':
                print(expert.get_api_usage_guide())
                continue
            
            if question.lower() in ['when', 'use cases']:
                print(expert.when_to_use_api())
                continue
            
            if question.lower() == 'stats':
                stats = expert.get_stats()
                print(f"\n📊 EXPERT STATS:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                continue
            
            answer = expert.ask_about_api(question)
            print(f"\n🎯 Expert: {answer}")
            
        except KeyboardInterrupt:
            print("\n👋 Happy coding with your request API!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_request_api_expert():
    """Demo the request API expert"""
    print("🎯 REQUEST SEARCH API EXPERT DEMO")
    print("=" * 40)
    
    expert = RequestSearchAPIAgent()
    
    demo_questions = [
        "What is this API used for?",
        "How do I get active requests?",
        "What does status ID 13 mean?",
        "How does pagination work?",
        "What authentication is required?",
        "When should I use this API?"
    ]
    
    print("\n❓ Demo Questions:")
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{i}. Q: {question}")
        answer = expert.ask_about_api(question)
        # Show first sentence
        first_sentence = answer.split('.')[0] + '.'
        print(f"   A: {first_sentence}")
    
    print(f"\n✅ The expert knows your request search API!")
    print(f"💡 Run interactively: python3 request_search_api_agent.py")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo_request_api_expert()
    else:
        interactive_request_api_expert()
