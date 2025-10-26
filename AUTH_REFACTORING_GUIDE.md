# Authentication Refactoring - BCE Architecture Alignment

## 📋 Overview

Your lecturer is correct: JWT token management and authentication logic are **CONTROL/ENTITY layer responsibilities**, not BOUNDARY layer.

**Refactoring Summary:**
- ✅ Moved ALL authentication logic to `User` entity (CONTROL layer)
- ✅ Simplified `AuthController` to HTTP-only (BOUNDARY layer)
- ✅ Created new `User.authenticate_user()` method with complete auth flow
- ✅ Maintained same API endpoints and responses

---

## 🏗️ Architecture Before vs After

### BEFORE: Mixed Concerns (Incorrect ❌)

```
BOUNDARY LAYER (auth_controller.py):
├─ Extract username, password, role_name from HTTP
├─ Validate role exists (Role.get_role_by_name) ❌ CONTROL logic
├─ Check credentials (User.check_login) ❌ CONTROL logic
├─ Verify role assignment ❌ CONTROL logic
├─ Create JWT token (User.create_session_token) ❌ CONTROL logic
├─ Format JSON response
└─ Send HTTP response

Problems:
- Controller mixing HTTP and business logic
- Hard to test business logic separately
- Hard to reuse authentication logic
```

### AFTER: Clean Separation (Correct ✅)

```
BOUNDARY LAYER (auth_controller.py):
├─ Extract data from HTTP request ✅
├─ Validate HTTP format (has required fields) ✅
├─ Call CONTROL layer: User.authenticate_user()
├─ Check CONTROL response
├─ Format JSON response ✅
└─ Send HTTP response ✅

         ↓↓↓ Delegates to ↓↓↓

CONTROL LAYER (user.py - User.authenticate_user):
├─ Verify user exists ✅ CONTROL logic
├─ Verify password ✅ CONTROL logic
├─ Verify user active ✅ CONTROL logic
├─ Verify role (if provided) ✅ CONTROL logic
├─ Generate JWT token ✅ CONTROL logic
├─ Update last_login timestamp ✅ CONTROL logic
└─ Return user + token ✅

Benefits:
- Controller only handles HTTP
- Business logic isolated in Entity
- Easy to test authentication separately
- Can call authenticate_user() from other controllers
```

---

## 📝 Code Changes

### 1. NEW Method in `src/entity/user.py`

Added `User.authenticate_user()` - Complete authentication with token generation

```python
@staticmethod
def authenticate_user(username: str, password: str, role_name: str = None) -> Optional[Dict]:
    """
    CONTROL LAYER: Complete authentication with token generation
    
    Handles ALL authentication logic:
    - Verify user exists
    - Verify password
    - Verify user is active
    - Verify role (if provided)
    - Generate JWT token
    - Update last_login timestamp
    
    Returns dict with user info and token, or None if authentication fails
    """
    try:
        # Step 1: Get user from database (ENTITY layer call)
        user = User.get_user_by_username(username)
        if not user:
            return None
        
        # Step 2: Verify password (CONTROL logic)
        if not check_password_hash(user['password'], password):
            return None
        
        # Step 3: Check if user account is active (CONTROL logic)
        if not user['is_active']:
            return None
        
        # Step 4: If role specified, verify user has that role (CONTROL logic)
        if role_name:
            from .role import Role
            role = Role.get_role_by_name(role_name)
            if not role or user['role_id'] != role['id']:
                return None
        
        # Step 5: Generate JWT token (TOKEN MANAGEMENT - CONTROL layer)
        token = User.create_session_token(user['id'])
        
        # Step 6: Update last_login timestamp (ENTITY layer call)
        supabase = get_supabase()
        supabase.table('users').update({
            "last_login": datetime.utcnow().isoformat()
        }).eq('id', user['id']).execute()
        
        # Step 7: Return authenticated user with token
        from .role import Role
        role = Role.get_role_by_id(user['role_id'])
        
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role_id': user['role_id'],
            'is_active': user['is_active'],
            'token': token,
            'role': role
        }
        
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        return None
```

**What This Method Does:**
1. ✅ Gets user by username (ENTITY - DB query)
2. ✅ Verifies password hash (CONTROL - business rule)
3. ✅ Checks if user is active (CONTROL - business rule)
4. ✅ Verifies role assignment (CONTROL - business rule)
5. ✅ Generates JWT token (CONTROL - token management)
6. ✅ Updates last_login (ENTITY - DB update)
7. ✅ Returns complete response (user + role + token)

---

### 2. SIMPLIFIED Controller in `src/controller/auth/auth_controller.py`

```python
class AuthController:
    """
    BOUNDARY LAYER: HTTP Interface for Authentication
    
    Responsible ONLY for:
    ✓ Extracting data from HTTP requests
    ✓ Validating HTTP format/structure
    ✓ Formatting HTTP responses
    ✓ Returning appropriate HTTP status codes
    
    ALL authentication logic delegated to CONTROL layer (Entity)
    """
    
    @auth_blueprint.route('/api/auth/login', methods=['POST'])
    def login():
        """
        BOUNDARY: Login endpoint
        
        Delegates to CONTROL layer which handles authentication
        """
        try:
            # ===== BOUNDARY: Extract HTTP request data =====
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            # ===== BOUNDARY: Validate required fields =====
            username = data.get('username')
            password = data.get('password')
            role_name = data.get('role_name')
            
            if not username or not password or not role_name:
                return jsonify({
                    'success': False,
                    'message': 'Username, password, and role_name are required'
                }), 400
            
            # ===== CALL CONTROL LAYER =====
            # User.authenticate_user() handles ALL authentication logic
            result = User.authenticate_user(username, password, role_name)
            
            # ===== BOUNDARY: Handle CONTROL layer response =====
            if not result:
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials or user role mismatch'
                }), 401
            
            # ===== BOUNDARY: Format HTTP response =====
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'token': result['token'],
                    'user': {
                        'id': result['id'],
                        'username': result['username'],
                        'full_name': result['full_name'],
                        'email': result['email'],
                        'role': {
                            'name': result['role']['role_name'],
                            'code': result['role']['role_code'],
                            'dashboard_route': result['role']['dashboard_route']
                        }
                    }
                }
            }), 200
        
        except Exception as e:
            # ===== BOUNDARY: Catch and format exceptions =====
            print(f"[ERROR] Login endpoint error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred during login'
            }), 500
```

**What This Controller Does:**
1. ✅ Extracts JSON from HTTP request (BOUNDARY)
2. ✅ Validates format/required fields (BOUNDARY)
3. ✅ Calls CONTROL layer: `User.authenticate_user()`
4. ✅ Checks result
5. ✅ Formats JSON response (BOUNDARY)
6. ✅ Returns HTTP response (BOUNDARY)

**What It Does NOT Do Anymore:**
- ❌ No password verification (moved to CONTROL)
- ❌ No token generation logic (moved to CONTROL)
- ❌ No business rule validation (moved to CONTROL)
- ❌ No authentication flow orchestration (moved to CONTROL)

---

## 🔄 Complete Login Flow - New Architecture

```
USER SUBMITS LOGIN FORM
        ↓
┌─────────────────────────────────────┐
│  FRONTEND (Next.js)                 │
│  - axios.post('/api/auth/login')    │
│  - {username, password, role_name}  │
└────────────┬────────────────────────┘
             ↓ HTTP POST
┌─────────────────────────────────────────────────────┐
│  BOUNDARY LAYER                                     │
│  (src/controller/auth/auth_controller.py)          │
│                                                     │
│  1. Extract JSON from request                       │
│  2. Validate format (has required fields)           │
│  3. Call User.authenticate_user()                   │
│     (DELEGATES TO CONTROL LAYER)                    │
│  4. Check response is not None                      │
│  5. Format JSON response                            │
│  6. Return HTTP 200 + token + user data             │
└────────────┬────────────────────────────────────────┘
             ↓ Returns result dict
┌─────────────────────────────────────────────────────┐
│  CONTROL LAYER                                      │
│  (src/entity/user.py - authenticate_user method)   │
│                                                     │
│  1. Verify user exists                              │
│  2. Verify password (check_password_hash)           │
│  3. Verify user is active                           │
│  4. Verify role assignment                          │
│  5. Generate JWT token (create_session_token)       │
│  6. Update last_login timestamp                     │
│  7. Get role details (Role.get_role_by_id)          │
│  8. Return {user, role, token}                      │
└────────────┬────────────────────────────────────────┘
             ↓ Database calls
┌─────────────────────────────────────────────────────┐
│  ENTITY LAYER                                       │
│  (Supabase PostgreSQL)                              │
│                                                     │
│  - SELECT * FROM users WHERE username=?             │
│  - SELECT * FROM roles WHERE id=?                   │
│  - UPDATE users SET last_login=? WHERE id=?         │
└─────────────────────────────────────────────────────┘
        ↑↑↑ Results returned ↑↑↑
        ↓↓↓ Back through layers ↓↓↓
┌─────────────────────────────────────────────────────┐
│  FRONTEND (Next.js)                                 │
│  - Receives HTTP 200 response                       │
│  - Extract token from response                      │
│  - Store token in localStorage                      │
│  - Redirect to dashboard                            │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Validation Checklist

After refactoring, verify:

- ✅ **BOUNDARY** (`auth_controller.py`):
  - Only extracts HTTP data
  - Only validates HTTP format
  - Only formats JSON responses
  - Only handles HTTP status codes
  - Delegates all business logic to CONTROL

- ✅ **CONTROL** (`user.py` - `authenticate_user`):
  - Contains all authentication logic
  - Handles password verification
  - Handles role verification
  - Handles token generation
  - Makes database calls through ENTITY layer

- ✅ **ENTITY** (`supabase_config.py`):
  - Contains raw database queries
  - No business logic
  - No HTTP handling
  - No token management

---

## 🧪 Testing the Refactoring

### Test 1: Valid Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin1",
    "password": "password123",
    "role_name": "User Admin"
  }'

Expected: 200 OK with token and user data
```

### Test 2: Invalid Password
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin1",
    "password": "wrongpassword",
    "role_name": "User Admin"
  }'

Expected: 401 Unauthorized (handled by CONTROL layer)
```

### Test 3: Missing Field
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin1",
    "role_name": "User Admin"
  }'

Expected: 400 Bad Request (handled by BOUNDARY layer)
```

### Test 4: Role Mismatch
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin1",
    "password": "password123",
    "role_name": "CSR Rep"
  }'

Expected: 401 Unauthorized (handled by CONTROL layer)
```

---

## 📊 Responsibilities After Refactoring

### BOUNDARY (HTTP Level)
```
✅ Request parsing
✅ HTTP format validation
✅ HTTP status codes
✅ JSON response formatting
✅ Exception catching
✅ Error HTTP responses
```

### CONTROL (Business Logic Level)
```
✅ User authentication
✅ Password verification
✅ Role verification
✅ User status checking
✅ JWT token generation
✅ Last login updates
✅ Business rule validation
✅ Exception throwing
```

### ENTITY (Data Level)
```
✅ Database queries
✅ Data persistence
✅ Data retrieval
✅ Direct SQL execution
```

---

## 🎯 Key Takeaways

1. **BOUNDARY layer** = HTTP interface (receives/sends HTTP)
2. **CONTROL layer** = Business logic (authentication, validation, token generation)
3. **ENTITY layer** = Database operations (CRUD to database)

**Your refactoring correctly:**
- ✅ Moved token generation to CONTROL
- ✅ Moved authentication logic to CONTROL
- ✅ Moved password verification to CONTROL
- ✅ Moved role verification to CONTROL
- ✅ Kept HTTP handling in BOUNDARY
- ✅ Kept database queries in ENTITY

This aligns with your lecturer's guidance and proper BCE architecture! 🎓

