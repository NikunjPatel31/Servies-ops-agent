# ITSM Qualification-Based Search API Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Qualification Types](#qualification-types)
3. [Operand Types](#operand-types)
4. [Operators](#operators)
5. [Value Types](#value-types)
6. [HTTP Request Examples](#http-request-examples)
7. [Request/Response Format](#requestresponse-format)
8. [Error Handling](#error-handling)

## Architecture Overview

The qualification-based search system provides a powerful and flexible way to query ITSM entities using complex filtering criteria. The complete request flow is:

```
HTTP Request → REST Controller → Service Layer → Repository Layer → Database
     ↓              ↓               ↓              ↓              ↓
SearchByQualRequest → RestConverters.toQual() → searchInfoPageByQualification() → JPA Predicates → SQL Query
```

### Key Components

1. **REST Controller**: `RequestController.searchRequestByQual()` handles `/api/request/search/byqual`
2. **Request Conversion**: `RestConverters.toQual()` converts REST qualifications to domain objects
3. **Service Layer**: `FlotoBaseServiceImpl.searchInfoPageByQualification()` processes business logic
4. **Repository Layer**: JPA repositories with qualification-based predicates
5. **Response**: `FlotoObjectPageRest<T>` with paginated results

## Qualification Types

The system supports 8 different qualification types, each serving specific use cases:

### 1. FlatQualificationRest
Contains a list of qualifications combined with implicit AND logic.

```json
{
  "type": "FlatQualificationRest",
  "quals": [
    // Array of QualificationRest objects
  ]
}
```

### 2. RelationalQualificationRest
The most common type - compares a left operand with a right operand using an operator.

```json
{
  "type": "RelationalQualificationRest",
  "leftOperand": { /* OperandRest */ },
  "operator": "Equal",
  "rightOperand": { /* OperandRest */ },
  "qualContext": null,
  "qualificationTag": null,
  "jsonKey": null
}
```

### 3. BinaryQualificationRest
Combines two qualifications with explicit AND/OR logic.

```json
{
  "type": "BinaryQualificationRest",
  "leftQual": { /* QualificationRest */ },
  "operator": "AND",
  "rightQual": { /* QualificationRest */ }
}
```

### 4. UnaryQualificationRest
Applies unary operators (IS_NULL, IS_NOT_NULL, etc.) to a single operand.

```json
{
  "type": "UnaryQualificationRest",
  "operand": { /* OperandRest */ },
  "operator": "IS_NOT_NULL",
  "qualContext": null
}
```

### 5. BatchQualificationRest
Similar to FlatQualificationRest but with explicit binary operator.

```json
{
  "type": "BatchQualificationRest",
  "quals": [ /* Array of QualificationRest */ ],
  "operator": "OR"
}
```

### 6. FlotoSubQueryRest
Enables sub-query operations for complex filtering.

```json
{
  "type": "FlotoSubQueryRest",
  "childQualification": { /* QualificationRest */ },
  "projectionField": "id",
  "sourceModel": "REQUEST",
  "mappingField": "requestId",
  "operator": "In",
  "tableName": "conversation"
}
```

### 7. KeywordQualificationRest
For full-text search operations.

### 8. FlotoJsonQualificationRest
For querying JSON fields within entities.

```json
{
  "type": "FlotoJsonQualificationRest",
  "jsonKey": "customData.field1",
  "qual": { /* QualificationRest */ }
}
```

## Operand Types

Operands represent the left and right sides of relational qualifications:

### 1. PropertyOperandRest
References entity properties using dot notation.

```json
{
  "type": "PropertyOperandRest",
  "key": "request.statusId"
}
```

**Common Property Keys:**
- `request.statusId` - Request status ID
- `request.name` - Request name/subject
- `request.requesterId` - Requester ID
- `request.technicianId` - Assigned technician ID
- `request.createdTime` - Creation timestamp
- `request.tags` - Request tags

### 2. ValueOperandRest
Contains actual values to compare against.

```json
{
  "type": "ValueOperandRest",
  "value": { /* ValueRest object */ }
}
```

### 3. CustomFieldOperandRest
References custom fields by name.

```json
{
  "type": "CustomFieldOperandRest",
  "fieldName": "Priority Level"
}
```

### 4. DbOperandRest
Direct database column references.

```json
{
  "type": "DbOperandRest",
  "key": "status_id",
  "parent": false
}
```

### 5. VariableOperandRest
References system variables.

```json
{
  "type": "VariableOperandRest",
  "value": "$CURRENT_USER_ID"
}
```

### 6. ExpressionOperandRest
Arithmetic expressions between operands.

```json
{
  "type": "ExpressionOperandRest",
  "left": { /* OperandRest */ },
  "operator": "ADD",
  "right": { /* OperandRest */ }
}
```

## Operators

### RelationalOperator Enum
The primary operators for comparing values:

| Operator | ID | Description | Example Use Case |
|----------|----|-----------|--------------------|
| `Equal` | 4 | Exact match | `status = 'Open'` |
| `Not_Equal` | 16 | Not equal | `status != 'Closed'` |
| `Like` | 6 | SQL LIKE pattern | `name LIKE '%urgent%'` |
| `Contains` | 20 | String contains | `description contains 'error'` |
| `Not_Contains` | 25 | String doesn't contain | `tags not contains 'spam'` |
| `Start_With` | 18 | String starts with | `name starts with 'INC'` |
| `End_With` | 19 | String ends with | `email ends with '@company.com'` |
| `In` | 7 | Value in list | `statusId in [1,2,3]` |
| `Not_In` | 17 | Value not in list | `statusId not in [13]` |
| `LessThan` | 0 | Less than | `createdTime < yesterday` |
| `LessThanOrEqual` | 1 | Less than or equal | `priority <= 3` |
| `GreaterThan` | 3 | Greater than | `createdTime > lastWeek` |
| `GreaterThanOrEqual` | 2 | Greater than or equal | `priority >= 2` |
| `Between` | 21 | Between two values | `createdTime between [start, end]` |
| `Before` | 26 | Date before | `dueDate before tomorrow` |
| `After` | 27 | Date after | `createdTime after lastMonth` |

**Case-Insensitive Variants:**
- `Equal_Case_Insensitive` (5)
- `Not_Equal_Case_Insensitive` (22)
- `In_Case_Insensitive` (23)
- `Not_In_Case_Insensitive` (24)

**Member Operations:**
- `Is_Member` (8) - Check if value is member of collection
- `All_Members_Exist` (9) - All values exist in collection
- `Any_Member_Or_All_Members_Exist` (10) - Any or all values exist
- `No_Members_Exist` (11) - No values exist in collection

### UnaryOperator Enum
For single-operand operations:

| Operator | ID | Description |
|----------|----|-----------| 
| `Is_Null` | 1 | Field is null |
| `Is_Not_Null` | 2 | Field is not null |
| `IS_EMPTY` | 3 | Collection is empty |
| `IS_NOT_EMPTY` | 4 | Collection is not empty |
| `IS_BLANK` | 5 | String is blank/empty |
| `IS_NOT_BLANK` | 6 | String is not blank |
| `Not` | 0 | Logical NOT |

### BinaryOperator Enum
For combining qualifications:

| Operator | ID | Description |
|----------|----|-----------| 
| `AND` | 0 | Logical AND |
| `OR` | 1 | Logical OR |

## Value Types

Value types represent the actual data being compared:

### Basic Value Types

#### StringValueRest
```json
{
  "type": "StringValueRest",
  "value": "Open"
}
```

#### LongValueRest
```json
{
  "type": "LongValueRest", 
  "value": 123
}
```

#### IntegerValueRest
```json
{
  "type": "IntegerValueRest",
  "value": 42
}
```

#### DoubleValueRest
```json
{
  "type": "DoubleValueRest",
  "value": 3.14
}
```

#### BooleanValueRest
```json
{
  "type": "BooleanValueRest",
  "value": true
}
```

### List Value Types

#### ListLongValueRest
```json
{
  "type": "ListLongValueRest",
  "value": [1, 2, 3, 13]
}
```

#### ListStringValueRest
```json
{
  "type": "ListStringValueRest", 
  "value": ["Open", "In Progress", "Resolved"]
}
```

#### ListIntegerValueRest
```json
{
  "type": "ListIntegerValueRest",
  "value": [1, 2, 3]
}
```

### Special Value Types

#### TimeValueRest
```json
{
  "type": "TimeValueRest",
  "value": "2024-01-15T10:30:00Z"
}
```

#### EnumValueRest
```json
{
  "type": "EnumValueRest",
  "value": "HIGH_PRIORITY"
}
```

#### FieldValueRest
```json
{
  "type": "FieldValueRest",
  "value": {
    "id": 123,
    "name": "Priority Field"
  }
}
```

## HTTP Request Examples

### 1. Simple Status Filtering (Not In)
Filter requests excluding specific status IDs:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=25&sort_by=createdTime' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [{
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "request.statusId"
        },
        "operator": "Not_In",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "ListLongValueRest",
            "value": [13, 14, 15]
          }
        }
      }]
    }
  }'
```

### 2. String Contains Search
Search requests containing specific text in subject:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=10' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [{
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "request.subject"
        },
        "operator": "Contains",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "StringValueRest",
            "value": "urgent"
          }
        }
      }]
    }
  }'
```

### 3. Multiple Conditions (AND Logic)
Filter by status AND requester:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=20' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [
        {
          "type": "RelationalQualificationRest",
          "leftOperand": {
            "type": "PropertyOperandRest",
            "key": "request.statusId"
          },
          "operator": "Equal",
          "rightOperand": {
            "type": "ValueOperandRest",
            "value": {
              "type": "LongValueRest",
              "value": 1
            }
          }
        },
        {
          "type": "RelationalQualificationRest",
          "leftOperand": {
            "type": "PropertyOperandRest",
            "key": "request.requesterId"
          },
          "operator": "Equal",
          "rightOperand": {
            "type": "ValueOperandRest",
            "value": {
              "type": "LongValueRest",
              "value": 456
            }
          }
        }
      ]
    }
  }'
```

### 4. OR Logic with Binary Qualification
Search for high priority OR critical requests:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=15' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "BinaryQualificationRest",
      "leftQual": {
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "request.priorityId"
        },
        "operator": "Equal",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "LongValueRest",
            "value": 1
          }
        }
      },
      "operator": "OR",
      "rightQual": {
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "request.urgencyId"
        },
        "operator": "Equal",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "LongValueRest",
            "value": 1
          }
        }
      }
    }
  }'
```

### 5. Null Check with Unary Qualification
Find requests without assigned technician:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=25' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [{
        "type": "UnaryQualificationRest",
        "operand": {
          "type": "PropertyOperandRest",
          "key": "request.technicianId"
        },
        "operator": "Is_Null"
      }]
    }
  }'
```

### 6. Date Range Filtering
Find requests created in the last 7 days:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=30' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [{
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "request.createdTime"
        },
        "operator": "GreaterThanOrEqual",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "TimeValueRest",
            "value": "2024-01-08T00:00:00Z"
          }
        }
      }]
    }
  }'
```

### 7. Custom Field Search
Search by custom field value:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=20' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [{
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "CustomFieldOperandRest",
          "fieldName": "Department"
        },
        "operator": "Equal",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "StringValueRest",
            "value": "IT Support"
          }
        }
      }]
    }
  }'
```

### 8. Tag-Based Filtering
Search requests with specific tags:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=25' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [{
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "request.tags"
        },
        "operator": "All_Members_Exist",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "ListStringValueRest",
            "value": ["urgent", "hardware"]
          }
        }
      }]
    }
  }'
```

### 9. Asset Search Example
Search hardware assets by name pattern:

```bash
curl 'http://your-server/api/asset/asset_hardware/search/byqual?offset=0&size=20' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [{
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "asset.name"
        },
        "operator": "Start_With",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "StringValueRest",
            "value": "LAPTOP-"
          }
        }
      }]
    }
  }'
```

### 10. User Search Example
Search users by email domain:

```bash
curl 'http://your-server/api/requester/search/byqual?offset=0&size=50' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "FlatQualificationRest",
      "quals": [{
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "user.email"
        },
        "operator": "End_With",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "StringValueRest",
            "value": "@company.com"
          }
        }
      }]
    }
  }'
```

### 11. Complex Nested Query
Multiple conditions with mixed operators:

```bash
curl 'http://your-server/api/request/search/byqual?offset=0&size=25&sort_by=createdTime' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "qualDetails": {
      "type": "BinaryQualificationRest",
      "leftQual": {
        "type": "FlatQualificationRest",
        "quals": [
          {
            "type": "RelationalQualificationRest",
            "leftOperand": {
              "type": "PropertyOperandRest",
              "key": "request.statusId"
            },
            "operator": "In",
            "rightOperand": {
              "type": "ValueOperandRest",
              "value": {
                "type": "ListLongValueRest",
                "value": [1, 2, 3]
              }
            }
          },
          {
            "type": "RelationalQualificationRest",
            "leftOperand": {
              "type": "PropertyOperandRest",
              "key": "request.priorityId"
            },
            "operator": "LessThanOrEqual",
            "rightOperand": {
              "type": "ValueOperandRest",
              "value": {
                "type": "LongValueRest",
                "value": 2
              }
            }
          }
        ]
      },
      "operator": "OR",
      "rightQual": {
        "type": "RelationalQualificationRest",
        "leftOperand": {
          "type": "PropertyOperandRest",
          "key": "request.subject"
        },
        "operator": "Contains",
        "rightOperand": {
          "type": "ValueOperandRest",
          "value": {
            "type": "StringValueRest",
            "value": "critical"
          }
        }
      }
    }
  }'
```

## Request/Response Format

### Complete Request Schema

```json
{
  "qualDetails": {
    "type": "QualificationRest",
    "description": "Optional description",
    // Qualification-specific properties based on type
  },
  "qualId": 0,           // Optional: Use predefined qualification by ID
  "columns": [],         // Optional: Specific columns to return
  "fullObject": false    // Optional: Return full object details
}
```

### URL Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `offset` | integer | 0 | Pagination offset |
| `size` | integer | 10 | Number of records per page |
| `sort_by` | string | null | Field to sort by (e.g., "createdTime", "name") |

### Response Schema

```json
{
  "objectList": [
    {
      "id": 123,
      "name": "Sample Request",
      "subject": "Request subject",
      "statusId": 1,
      "priorityId": 2,
      "requesterId": 456,
      "technicianId": 789,
      "createdTime": "2024-01-15T10:30:00Z",
      "updatedTime": "2024-01-15T14:20:00Z",
      // ... other request fields
    }
  ],
  "totalCount": 1
}
```

### Common Response Fields

**Request Entity Fields:**
- `id` - Unique identifier
- `name` - Request name/title
- `subject` - Request subject
- `description` - Detailed description
- `statusId` - Current status ID
- `priorityId` - Priority level ID
- `urgencyId` - Urgency level ID
- `impactId` - Impact level ID
- `requesterId` - Requester user ID
- `technicianId` - Assigned technician ID
- `groupId` - Assigned group ID
- `categoryId` - Category ID
- `subCategoryId` - Sub-category ID
- `itemId` - Service catalog item ID
- `createdTime` - Creation timestamp
- `updatedTime` - Last update timestamp
- `dueByTime` - Due date timestamp
- `tags` - Array of tags
- `customFields` - Custom field values

## Error Handling

### Common Error Scenarios

#### 1. Invalid Operator for Value Type
**Error:** Using string operators with numeric values
```json
{
  "error": "Invalid operator 'Contains' for value type 'LongValueRest'",
  "code": "INVALID_OPERATOR_VALUE_TYPE",
  "status": 400
}
```

#### 2. Invalid Property Key
**Error:** Referencing non-existent property
```json
{
  "error": "Property 'request.invalidField' not found",
  "code": "INVALID_PROPERTY_KEY",
  "status": 400
}
```

#### 3. Malformed JSON Structure
**Error:** Missing required fields or invalid JSON
```json
{
  "error": "Required field 'leftOperand' missing in RelationalQualificationRest",
  "code": "MALFORMED_QUALIFICATION",
  "status": 400
}
```

#### 4. Authentication/Authorization Errors
**Error:** Invalid or missing JWT token
```json
{
  "error": "Authentication required",
  "code": "UNAUTHORIZED",
  "status": 401
}
```

#### 5. Permission Denied
**Error:** User lacks permission to access resource
```json
{
  "error": "Insufficient permissions to access requests",
  "code": "FORBIDDEN",
  "status": 403
}
```

### Best Practices

1. **Always validate property keys** against the entity schema before sending requests
2. **Use appropriate value types** for each operator (e.g., ListLongValueRest for In/Not_In with numeric IDs)
3. **Handle pagination** properly using offset and size parameters
4. **Include proper authentication** headers with valid JWT tokens
5. **Use FlatQualificationRest** for simple AND logic between multiple conditions
6. **Use BinaryQualificationRest** when you need explicit OR logic
7. **Test qualifications** with small datasets first to verify correctness
8. **Cache frequently used qualifications** using the qualId parameter
9. **Use appropriate sort_by fields** to ensure consistent ordering
10. **Handle empty results** gracefully when totalCount is 0

### Performance Considerations

- **Limit page size** to reasonable values (typically 10-100 records)
- **Use indexed fields** in property operands when possible
- **Avoid complex nested qualifications** for better performance
- **Consider using qualId** for frequently executed searches
- **Use specific columns** parameter to reduce data transfer when full objects aren't needed

---

This documentation provides comprehensive coverage of the ITSM qualification-based search API. For additional examples or specific use cases, refer to the test cases in the codebase or contact the development team.
