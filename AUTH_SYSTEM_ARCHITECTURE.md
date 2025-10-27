# 🔐 Authentication System Architecture

## Overview: How 4 Controllers Work Together

Your authentication system has **4 key components**:

1. **auth_controller.py** - Main HTTP handler (BOUNDARY layer)
2. **login_controller.py** - Legacy login endpoint (BOUNDARY layer)
3. **logout_controller.py** - Legacy logout endpoint (BOUNDARY layer)
4. **auth_middleware.py** - Request interceptor for protected routes (BOUNDARY layer)

---

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React/Next.js)                   │
│                                                                   │
│  1. User submits login form                                      │
│  2. Axios sends POST /api/auth/login with credentials            │
│  3. Receives JWT token in response                               │
│  4. Stores token in localStorage                                 │
│  5. Sends token in Authorization header for protected routes     │
│  6. Clicks logout → POST /api/auth/logout with token             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    HTTP Request/Response
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ↓                                   ↓
    ┌─────────────────┐         ┌──────────────────────┐
    │ auth_controller │         │ auth_middleware      │
    │ (Main)          │         │ (Protected Routes)   │
    └────────┬────────┘         └──────────┬───────────┘
             │                             │
    Routes: │                    Protects: │
    - /api/auth/login              - All /api/* endpoints
    - /api/auth/logout             - Verifies JWT token
    - /api/auth/verify             - Checks user role
             │                             │
             └──────────────┬──────────────┘
                            │
                   Calls CONTROL Layer
                            │
         ┌──────────────────┴──────────────────┐
         │                                     │
         ↓                                     ↓
    ┌────────────────────┐        ┌──────────────────────┐
    │ User Entity        │        │ Role Entity          │
    │ (CONTROL Logic)    │        │ (CONTROL Logic)      │
    └────────────────────┘        └──────────────────────┘
         │                             │
    Methods:                      Methods:
    - authenticate_user()         - get_role_by_name()
    - verify_session_token()      - get_role_by_id()
    - invalidate_session_token()
         │                             │
         └──────────────┬──────────────┘
                        │
              Database (Supabase)
```

---

## 🔄 Request Flow: Step-by-Step

### Flow 1: LOGIN Process

```
STEP 1: Frontend Sends Login Request
┌──────────────────────────────────────┐
│ POST /api/auth/login                 │
│ {                                    │
│   "username": "admin1",              │
│   "password": "SecurePass123",       │
│   "role_name": "User Admin"          │
│ }                                    │
└────────────────────┬─────────────────┘
                     │
                     ↓ Routes to
        ┌─────────────────────────────┐
        │ auth_controller.login()     │
        │ (Line 39-128)               │
        └─────────────────┬───────────┘
                          │
STEP 2: BOUNDARY Validation (auth_controller)
┌──────────────────────────────────────────────────┐
│ 1. RequestHelpers.validate_json_body()           │
│    ✓ Check if request has JSON body              │
│                                                  │
│ 2. RequestHelpers.get_json_data()                │
│    ✓ Extract JSON safely                         │
│                                                  │
│ 3. RequestHelpers.validate_required_fields()     │
│    ✓ Check: username, password, role_name       │
│                                                  │
│ 4. Sanitizers.sanitize_*()                       │
│    ✓ Clean input data                            │
│                                                  │
│ 5. Validators.validate_username()                │
│    ✓ Check format (3-20 chars, alphanumeric)    │
│                                                  │
│ 6. Validators.validate_password()                │
│    ✓ Check strength (8+ chars, upper, lower)    │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓ All valid, call CONTROL layer
        ┌─────────────────────────────────────────┐
        │ User.authenticate_user()                │
        │ (CONTROL Layer - user.py)               │
        └─────────────────┬───────────────────────┘
                          │
STEP 3: CONTROL Logic (User Entity)
┌──────────────────────────────────────────────────┐
│ 1. User.get_user_by_username("admin1")           │
│    → Query DB: users table                       │
│    ← Returns user object (id, username, etc)    │
│                                                  │
│ 2. check_password_hash(stored, provided)         │
│    ✓ Verify password matches                     │
│                                                  │
│ 3. Check user['is_active']                       │
│    ✓ Ensure user account is active              │
│                                                  │
│ 4. Role.get_role_by_name("User Admin")           │
│    → Query DB: roles table                       │
│    ← Returns role object                         │
│                                                  │
│ 5. Verify user['role_id'] == role['id']         │
│    ✓ User has correct role                       │
│                                                  │
│ 6. User.create_session_token(user_id)            │
│    ✓ Generate JWT token (expires in 24h)        │
│    ✓ Token contains: {user_id, exp, iat}       │
│                                                  │
│ 7. Update last_login timestamp                   │
│                                                  │
│ 8. Return authentication response                │
│    {id, username, email, token, role}           │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓ Returns to BOUNDARY
        ┌─────────────────────────────────────────┐
        │ BACK in auth_controller.login()         │
        └─────────────────┬───────────────────────┘
                          │
STEP 4: BOUNDARY Response Formatting
┌──────────────────────────────────────────────────┐
│ 1. Check result is not None (success)            │
│                                                  │
│ 2. Format response data:                         │
│    {                                             │
│      "token": "eyJ0eXAi...",                     │
│      "user": {                                   │
│        "id": 1,                                  │
│        "username": "admin1",                     │
│        "email": "admin@csr.com",                 │
│        "role": {                                 │
│          "name": "User Admin",                   │
│          "code": "admin",                        │
│          "dashboard_route": "/admin"             │
│        }                                         │
│      }                                           │
│    }                                             │
│                                                  │
│ 3. Log activity: User.log_user_activity()       │
│                                                  │
│ 4. ResponseHelpers.success_response()           │
│    Returns HTTP 200 with response               │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓ HTTP Response
        ┌─────────────────────────────────────────┐
        │ HTTP 200 OK                             │
        │ {                                       │
        │   "success": true,                      │
        │   "data": {token, user},                │
        │   "message": "Login successful"         │
        │ }                                       │
        └─────────────────┬───────────────────────┘
                          │
                          ↓ Frontend receives
        ┌─────────────────────────────────────────┐
        │ Frontend stores token in localStorage   │
        │ Redirects user to dashboard             │
        │ Token used in all future requests       │
        └─────────────────────────────────────────┘
```

---

### Flow 2: VERIFY Session (Protected Route Access)

```
STEP 1: Frontend Sends API Request with Token
┌────────────────────────────────────────────────┐
│ GET /api/userAccount                           │
│ Headers: {                                     │
│   "Authorization": "Bearer eyJ0eXAi..."       │
│ }                                              │
└────────────────────┬───────────────────────────┘
                     │
                     ↓ INTERCEPTED by
        ┌─────────────────────────────────────────┐
        │ auth_middleware.require_role()          │
        │ (auth_middleware.py - BOUNDARY layer)   │
        └─────────────────┬───────────────────────┘
                          │
STEP 2: BOUNDARY Token Validation (Middleware)
┌──────────────────────────────────────────────────┐
│ 1. TokenHelpers.validate_bearer_format()         │
│    ✓ Check header format: "Bearer {token}"      │
│                                                  │
│ 2. TokenHelpers.extract_bearer_token()           │
│    ✓ Extract token from header                   │
│                                                  │
│ 3. Call CONTROL layer to verify token           │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓
        ┌─────────────────────────────────────────┐
        │ User.verify_session_token(token)        │
        │ (CONTROL Layer - user.py)               │
        └─────────────────┬───────────────────────┘
                          │
STEP 3: CONTROL Logic (Token Verification)
┌──────────────────────────────────────────────────┐
│ 1. jwt.decode(token, SUPABASE_KEY, 'HS256')    │
│    ✓ Verify token signature                     │
│    ✓ Check token not expired                    │
│    ✓ Extract user_id from payload               │
│                                                  │
│ 2. User.get_by_id(user_id)                      │
│    → Query DB for user                          │
│    ← Returns user object                        │
│                                                  │
│ 3. Return user object (or None if invalid)      │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓ Back to middleware
        ┌─────────────────────────────────────────┐
        │ auth_middleware checks result           │
        └─────────────────┬───────────────────────┘
                          │
STEP 4: Middleware Authorization Check
┌──────────────────────────────────────────────────┐
│ 1. If user not found → Return HTTP 401           │
│                                                  │
│ 2. If required_roles specified (e.g., 'admin')  │
│    ✓ Get user's role from DB                    │
│    ✓ Check if user has required role            │
│    ✗ If not → Return HTTP 403 (Forbidden)       │
│                                                  │
│ 3. All checks pass → Allow request to proceed   │
│    ✓ Add user to request context                │
│    ✓ Call next route handler                    │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓
        ┌─────────────────────────────────────────┐
        │ Route handler executes normally         │
        │ (e.g., view_user_account_controller)    │
        └─────────────────────────────────────────┘
```

---

### Flow 3: LOGOUT Process

```
STEP 1: Frontend Sends Logout Request
┌──────────────────────────────────────┐
│ POST /api/auth/logout                │
│ Headers: {                           │
│   "Authorization": "Bearer ..."      │
│ }                                    │
└────────────────────┬─────────────────┘
                     │
                     ↓ Routes to
        ┌─────────────────────────────┐
        │ auth_controller.logout()    │
        │ (Line 130-168)              │
        └─────────────────┬───────────┘
                          │
STEP 2: BOUNDARY Token Extraction
┌──────────────────────────────────────────────────┐
│ 1. Get Authorization header                      │
│                                                  │
│ 2. TokenHelpers.validate_bearer_format()         │
│    ✓ Verify format: "Bearer {token}"             │
│                                                  │
│ 3. TokenHelpers.extract_bearer_token()           │
│    ✓ Extract token safely                        │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓
        ┌─────────────────────────────┐
        │ User.invalidate_session_    │
        │ token(token)                │
        │ (CONTROL Layer)             │
        └─────────────────┬───────────┘
                          │
STEP 3: CONTROL Logic (Token Invalidation)
┌──────────────────────────────────────────────────┐
│ 1. jwt.decode(token, ...)                        │
│    ✓ Verify token signature                      │
│    ✓ Extract user_id from payload                │
│                                                  │
│ 2. Log activity: Token invalidated               │
│                                                  │
│ 3. Return success (True)                         │
│                                                  │
│ Note: JWT is stateless, so we just verify       │
│       In future: Add to token blacklist DB      │
└────────────────────┬─────────────────────────────┘
                     │
                     ↓ Back to BOUNDARY
        ┌─────────────────────────────────────────┐
        │ auth_controller formats response         │
        │                                         │
        │ ResponseHelpers.success_response()      │
        │ Returns HTTP 200                        │
        └─────────────────┬───────────────────────┘
                          │
                          ↓
        ┌─────────────────────────────────────────┐
        │ Frontend receives logout confirmation   │
        │ Removes token from localStorage         │
        │ Redirects to login page                 │
        └─────────────────────────────────────────┘
```

---

## 📁 File Structure & Responsibilities

### auth_controller.py (MAIN - Lines 1-250)
**Location:** `src/controller/auth/auth_controller.py`

**Purpose:** Primary HTTP handler for authentication

**Methods:**
1. `login()` - Lines 39-128
   - Extract JSON from request
   - Validate format and fields
   - Sanitize input
   - Validate data format
   - Delegate to User.authenticate_user()
   - Format and return response

2. `logout()` - Lines 130-168
   - Extract Authorization header
   - Validate bearer format
   - Delegate to User.invalidate_session_token()
   - Return success/failure

3. `verify_session()` - Lines 170-244
   - Extract Authorization header
   - Validate bearer format
   - Delegate to User.verify_session_token()
   - Get role information
   - Format and return user data

---

### auth_middleware.py (ROUTE PROTECTION)
**Location:** `src/controller/auth/auth_middleware.py`

**Purpose:** Protect routes with JWT verification

**How It Works:**
```python
@auth_blueprint.before_request
def require_auth():
    # Intercepts ALL requests to protected routes
    # Verifies JWT token
    # Checks user role if required
    # Allows or blocks request
```

**Usage in other controllers:**
```python
@some_controller.route('/api/users')
@require_role('admin')  # Decorator that uses middleware
def get_users():
    # Only admins can access
```

---

### login_controller.py (LEGACY)
**Location:** `src/controller/auth/login_controller.py`

**Status:** LEGACY (superseded by auth_controller.login())

**Why it exists:** 
- May be for backward compatibility
- Or redundant code from earlier development

**Note:** Use `auth_controller.login()` instead

---

### logout_controller.py (LEGACY)
**Location:** `src/controller/auth/logout_controller.py`

**Status:** LEGACY (superseded by auth_controller.logout())

**Why it exists:**
- May be for backward compatibility
- Or redundant code from earlier development

**Note:** Use `auth_controller.logout()` instead

---

## 🔄 Interaction Summary Table

| Component | Role | What It Does | Calls |
|-----------|------|------------|-------|
| **auth_controller** | BOUNDARY | HTTP handler, validation, response formatting | User.authenticate_user(), User.verify_session_token(), User.invalidate_session_token() |
| **auth_middleware** | BOUNDARY | Route protection, token verification | User.verify_session_token() |
| **login_controller** | LEGACY | Old login endpoint (redundant) | - |
| **logout_controller** | LEGACY | Old logout endpoint (redundant) | - |
| **User Entity** | CONTROL | Authentication logic, token generation | Database queries, JWT operations |
| **Role Entity** | CONTROL | Role operations | Database queries |

---

## 🎯 Key Points

✅ **BOUNDARY Layer (Controllers):**
- Extract HTTP request data
- Validate format and presence
- Sanitize input
- Call CONTROL layer

✅ **CONTROL Layer (Entities):**
- Perform business logic
- Verify credentials
- Generate tokens
- Interact with database

✅ **Middleware:**
- Intercepts requests
- Verifies authentication
- Checks authorization
- Protects routes

✅ **Token Flow:**
1. Generated in: `User.create_session_token()`
2. Validated in: `User.verify_session_token()`
3. Extracted in: `TokenHelpers.extract_bearer_token()`
4. Used in: All protected endpoints via middleware

---

## 🔐 Security Implementation

```
User Input
    ↓
JSON Validation (RequestHelpers)
    ↓
Required Fields Check (RequestHelpers)
    ↓
Input Sanitization (Sanitizers)
    ↓
Format Validation (Validators)
    ↓
CONTROL Logic (User Entity)
    ↓
Response Formatting (ResponseHelpers)
    ↓
HTTP Response with Status Code
```

---

## 📊 Complete Request Lifecycle

```
┌─ Frontend ─────────────────────────────────────────────────────┐
│                                                               │
│  1. POST /api/auth/login with credentials                    │
│                              ↓                                │
├──────────────────────────────────────────────────────────────┤
│           BOUNDARY Layer (auth_controller)                   │
│                                                               │
│  2. Validate JSON format                                     │
│  3. Extract JSON data                                        │
│  4. Validate required fields                                 │
│  5. Sanitize input                                           │
│  6. Validate format (username, password)                     │
│                              ↓                                │
├──────────────────────────────────────────────────────────────┤
│          CONTROL Layer (User Entity)                         │
│                                                               │
│  7. Get user by username                                     │
│  8. Verify password                                          │
│  9. Check user active                                        │
│  10. Verify role                                             │
│  11. Generate JWT token                                      │
│  12. Update last_login                                       │
│                              ↓                                │
├──────────────────────────────────────────────────────────────┤
│          BOUNDARY Layer (Response)                           │
│                                                               │
│  13. Format response data                                    │
│  14. Add HTTP status code (200)                              │
│  15. Return JSON response with token                         │
│                              ↓                                │
│  16. Frontend receives token and stores in localStorage      │
│  17. Frontend adds token to Authorization header for         │
│      subsequent requests                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎓 For Your Sequence Diagram

**Actors:**
1. User (Frontend)
2. auth_controller (BOUNDARY)
3. auth_middleware (BOUNDARY)
4. User Entity (CONTROL)
5. Database

**Sequence for Login:**
```
User → auth_controller: POST /api/auth/login
auth_controller → Validators: validate_username()
auth_controller → Sanitizers: sanitize_data()
auth_controller → User Entity: authenticate_user()
User Entity → Database: get_user_by_username()
User Entity → User Entity: create_session_token()
User Entity → auth_controller: return {user + token}
auth_controller → User: HTTP 200 {token}
```

**Sequence for Protected Route:**
```
User → auth_middleware: GET /api/userAccount (with token)
auth_middleware → User Entity: verify_session_token()
User Entity → Database: get_user(user_id)
User Entity → auth_middleware: return user
auth_middleware → Route Handler: proceed with request
Route Handler → User: HTTP 200 {data}
```

