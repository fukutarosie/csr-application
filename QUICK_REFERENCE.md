# ⚡ Quick Reference - Controller Improvements

## New Files Created

```
src/utils/
├── validators.py        (250 lines)  - All validation functions
├── sanitizers.py        (180 lines)  - All sanitization functions
└── helpers.py          (400 lines)  - BOUNDARY layer helpers
```

---

## Import Statements

Add these to your controllers:

```python
# For validation
from src.utils.validators import Validators, ProfileValidators

# For sanitization
from src.utils.sanitizers import Sanitizers

# For helpers
from src.utils.helpers import (
    TokenHelpers,
    RequestHelpers,
    ResponseHelpers,
    DataHelpers,
    PaginationHelpers
)
```

---

## Validation Quick Reference

```python
# Validate individual fields
Validators.validate_email(email)           # Returns (bool, str)
Validators.validate_username(username)     # Returns (bool, str)
Validators.validate_password(password)     # Returns (bool, str)
Validators.validate_full_name(full_name)   # Returns (bool, str)
Validators.validate_phone(phone)           # Returns (bool, str)
Validators.validate_role_id(role_id)       # Returns (bool, str)

# Validate bulk data
Validators.validate_user_data(
    username, password, email, full_name, role_id, phone
)  # Returns (bool, str)

Validators.validate_user_update(updates_dict)  # Returns (bool, str)
```

---

## Sanitization Quick Reference

```python
# Sanitize individual fields
Sanitizers.sanitize_email(email)           # Trim, lowercase
Sanitizers.sanitize_username(username)     # Trim, lowercase, max 20
Sanitizers.sanitize_full_name(full_name)   # Trim, preserve case
Sanitizers.sanitize_phone(phone)           # Keep digits, separators
Sanitizers.sanitize_address(address)       # Trim, max 200

# Sanitize entire objects
Sanitizers.sanitize_user_data(data)        # Sanitize all user fields
Sanitizers.sanitize_profile_data(data)     # Sanitize all profile fields

# HTML escape
Sanitizers.html_escape(text)               # Escape <, >, &, etc.
```

---

## Helper Functions Quick Reference

### Token Helpers
```python
# Validate header format
is_valid, error = TokenHelpers.validate_bearer_format(auth_header)

# Extract token
token = TokenHelpers.extract_bearer_token(auth_header)

# Get token from request
token = TokenHelpers.get_token_from_request()
```

### Request Helpers
```python
# Validate JSON body
is_valid, error = RequestHelpers.validate_json_body()

# Get JSON data safely
data = RequestHelpers.get_json_data()

# Validate required fields
is_valid, error, missing = RequestHelpers.validate_required_fields(
    data, ['field1', 'field2']
)
```

### Response Helpers
```python
# Success response
response, status = ResponseHelpers.success_response(
    data={'key': 'value'},
    message='Success message',
    status_code=200
)
return jsonify(response), status

# Error response
response, status = ResponseHelpers.error_response(
    message='Error message',
    error_code='ERROR_CODE',
    status_code=400
)
return jsonify(response), status

# Validation error
response, status = ResponseHelpers.validation_error_response(
    ['Error 1', 'Error 2'],
    status_code=400
)
return jsonify(response), status
```

### Data Helpers
```python
# Format for response (removes password)
user_response = DataHelpers.format_user_response(user, include_role=True)

# Format profile for response
profile_response = DataHelpers.format_profile_response(profile)

# Exclude sensitive fields
public_data = DataHelpers.exclude_fields(user, ['password_hash'])

# Include only specific fields
limited_data = DataHelpers.include_only_fields(user, ['id', 'username'])
```

### Pagination Helpers
```python
# Get pagination from query string: ?page=2&limit=10
page, limit = PaginationHelpers.get_pagination_params()

# Create pagination metadata
meta = PaginationHelpers.create_pagination_meta(
    total_items=150,
    page=2,
    limit=10
)
```

---

## Entity Business Logic Quick Reference

```python
# User entity new methods
User.invalidate_session_token(token)        # Invalidate token
User.get_user_complete_details(user_id)     # Get user + profile + role
User.get_all_active_users()                 # Get active users only
User.get_users_by_role(role_id)             # Get users by role
User.get_users_by_role_name(role_name)      # Get users by role name
User.count_users()                          # Total user count
User.count_active_users()                   # Active user count
User.email_exists(email)                    # Check email uniqueness
User.username_exists(username)              # Check username uniqueness
User.get_user_login_history(user_id, limit) # Get login history
User.log_user_activity(user_id, type, details)  # Log activity
```

---

## Common Validation Patterns

### Pattern 1: Validate Single Field
```python
is_valid, error_msg = Validators.validate_email(email)
if not is_valid:
    response, status = ResponseHelpers.error_response(
        message=error_msg,
        error_code='INVALID_EMAIL',
        status_code=400
    )
    return jsonify(response), status
```

### Pattern 2: Validate All User Fields
```python
is_valid, error_msg = Validators.validate_user_data(
    username, password, email, full_name, role_id, phone
)
if not is_valid:
    response, status = ResponseHelpers.error_response(
        message=error_msg,
        error_code='VALIDATION_ERROR',
        status_code=400
    )
    return jsonify(response), status
```

### Pattern 3: Validate Required Fields
```python
is_valid, error_msg, missing = RequestHelpers.validate_required_fields(
    data, ['username', 'password', 'email']
)
if not is_valid:
    response, status = ResponseHelpers.error_response(
        message=error_msg,
        error_code='MISSING_FIELDS',
        status_code=400,
        details={'missing_fields': missing}
    )
    return jsonify(response), status
```

### Pattern 4: Sanitize and Validate
```python
# Sanitize
sanitized = Sanitizers.sanitize_user_data(data)

# Validate
is_valid, error = Validators.validate_username(sanitized['username'])
if not is_valid:
    return error_response(error, status_code=400)

# Use sanitized data
user = User.create_user(
    username=sanitized['username'],
    email=sanitized['email'],
    ...
)
```

### Pattern 5: Check Uniqueness
```python
# Check if email exists
if User.email_exists(email):
    return error_response('Email already exists', status_code=400)

# Check if username exists
if User.username_exists(username):
    return error_response('Username already exists', status_code=400)

# Then create user
user = User.create_user(...)
```

---

## Common Error Codes

```python
# Authentication
'AUTH_FAILED'           - Login failed (invalid credentials)
'INVALID_TOKEN'         - Token invalid or expired
'INVALID_TOKEN_FORMAT'  - Bearer token format invalid
'NO_TOKEN'              - Token not provided

# Validation
'VALIDATION_ERROR'      - General validation error
'INVALID_EMAIL'         - Email format invalid
'INVALID_USERNAME'      - Username format invalid
'INVALID_PASSWORD'      - Password format/strength invalid
'MISSING_FIELDS'        - Required fields missing

# Data
'DUPLICATE_EMAIL'       - Email already exists
'DUPLICATE_USERNAME'    - Username already exists
'NOT_FOUND'             - Resource not found
'CREATION_FAILED'       - Failed to create resource

# Server
'SERVER_ERROR'          - General server error
'EMPTY_BODY'            - Request body empty
'INVALID_JSON'          - Invalid JSON format
```

---

## HTTP Status Codes

```python
200  # Success, OK
201  # Created (POST successful)
400  # Bad Request (validation error)
401  # Unauthorized (auth failed, invalid token)
403  # Forbidden (no permission)
404  # Not Found
409  # Conflict (duplicate resource)
500  # Internal Server Error
```

---

## Validation Rules Summary

| Field | Min | Max | Requirements |
|-------|-----|-----|--------------|
| username | 3 | 20 | alphanumeric, -, _ |
| password | 8 | 100 | upper, lower, digit |
| email | - | 100 | valid format |
| full_name | 2 | 100 | must have letter |
| phone | 10 digits | - | standard format |
| address | 5 | 200 | - |
| role_id | - | - | positive integer |

---

## Before & After Code Example

### BEFORE
```python
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'email']):
        return {'error': 'Missing fields'}, 400
    
    user = User.create_user(
        username=data['username'],
        email=data['email']
    )
    
    return {'user': user}, 201
```

### AFTER
```python
@app.route('/api/users', methods=['POST'])
def create_user():
    # Validate JSON
    data = RequestHelpers.get_json_data()
    if not data:
        return error_response('Empty body'), 400
    
    # Validate required fields
    is_valid, error, _ = RequestHelpers.validate_required_fields(
        data, ['username', 'email']
    )
    if not is_valid:
        return error_response(error), 400
    
    # Sanitize
    sanitized = Sanitizers.sanitize_user_data(data)
    
    # Validate format
    is_valid, error = Validators.validate_username(sanitized['username'])
    if not is_valid:
        return error_response(error), 400
    
    is_valid, error = Validators.validate_email(sanitized['email'])
    if not is_valid:
        return error_response(error), 400
    
    # Check uniqueness
    if User.email_exists(sanitized['email']):
        return error_response('Email already exists'), 409
    
    # Create
    user = User.create_user(
        username=sanitized['username'],
        email=sanitized['email']
    )
    
    if user:
        response, status = ResponseHelpers.success_response(
            data=DataHelpers.format_user_response(user),
            message='User created',
            status_code=201
        )
        return jsonify(response), status
    
    return error_response('Creation failed'), 400
```

---

## Documentation Files

- **`CONTROLLER_IMPROVEMENTS_GUIDE.md`** - Comprehensive guide (600+ lines)
- **`IMPROVEMENTS_SUMMARY.md`** - Summary with benefits
- **`CONTROLLER_COMPARISON_ANALYSIS.md`** - Before/after comparison
- **`CONTROLLER_ANALYSIS_COMPLETE.md`** - Initial analysis

---

## Tips & Best Practices

✅ **Always sanitize input** before validation
✅ **Always validate** before using in CONTROL layer
✅ **Always check uniqueness** before creating
✅ **Always log activities** for audit trail
✅ **Always return specific error codes**
✅ **Always format responses** using helpers
✅ **Never expose password** in responses
✅ **Never mix validation in CONTROL**
✅ **Never skip error handling**
✅ **Never hardcode validation rules**

---

**Your controllers are now production-ready! 🚀**

