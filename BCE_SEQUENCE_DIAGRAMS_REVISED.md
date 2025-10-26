# BCE Sequence Diagrams - REVISED (Post-Authentication Refactoring)

**Last Updated:** October 26, 2025  
**Status:** Updated to reflect refactored authentication system

---

## 1. BASIC LOGIN FLOW - SEQUENCE DIAGRAM

### Sequence: User logs in with username, password, and role

```
┌─────────────┬───────────────────┬─────────────────┬──────────────────┬──────────────────┐
│  Frontend   │ AuthController    │ User Entity     │  Role Entity     │   PostgreSQL     │
│  (Browser)  │  (BOUNDARY)       │  (CONTROL)      │   (ENTITY)       │    Database      │
└─────────────┴───────────────────┴─────────────────┴──────────────────┴──────────────────┘
       │                │                 │                 │                 │
       │                │                 │                 │                 │
       │ (1) POST /api/auth/login        │                 │                 │
       │ {username, password, role_name}│                 │                 │
       ├───────────────────────────────→│                 │                 │
       │                │                 │                 │                 │
       │                │ (2) Extract JSON data              │                 │
       │                │ - username: 'admin1'               │                 │
       │                │ - password: 'pass123'              │                 │
       │                │ - role_name: 'User Admin'          │                 │
       │                │                 │                 │                 │
       │                │ (3) Validate required fields       │                 │
       │                │ - All fields present? ✓            │                 │
       │                │ - Valid data types? ✓              │                 │
       │                │                 │                 │                 │
       │                │ (4) Delegate to CONTROL layer      │                 │
       │                │ User.authenticate_user(...)        │                 │
       │                ├────────────────→│                 │                 │
       │                │                 │                 │                 │
       │                │ (5) CONTROL: Get user              │                 │
       │                │ User.get_user_by_username('admin1')│                 │
       │                │ (ENTITY operation)                 │                 │
       │                │                 │                 │                 │
       │                │ (6) ENTITY: Query database         │                 │
       │                │                 ├─ SELECT * FROM users WHERE ...    │
       │                │                 │ username='admin1' ───────────────→│
       │                │                 │                 │                 │
       │                │                 │                 │ (7) Return user │
       │                │                 │                 │     {id: '123', │
       │                │                 │                 │      username:  │
       │                │                 │                 │      'admin1',  │
       │                │                 │←─────────────────┤    password_hash│
       │                │                 │ Return Dict     │    '...',       │
       │                │←────────────────┤ with user data  │    is_active:   │
       │                │                 │                 │    true, ...}   │
       │                │                 │                 │                 │
       │                │ (8) CONTROL: Check password        │                 │
       │                │ check_password_hash('pass123',     │                 │
       │                │   user['password_hash'])           │                 │
       │                │ → True ✓                           │                 │
       │                │                 │                 │                 │
       │                │ (9) CONTROL: Check user active     │                 │
       │                │ if user['is_active']:              │                 │
       │                │ → True ✓                           │                 │
       │                │                 │                 │                 │
       │                │ (10) CONTROL: Get role             │                 │
       │                │ Role.get_role_by_name('User Admin')│                 │
       │                │ (ENTITY operation)                 │                 │
       │                │                 │ ────────────────→│ SELECT * FROM  │
       │                │                 │                 │ roles WHERE ... │
       │                │                 │                 │ role_name=...   │
       │                │                 │                 ├──────────────→ │
       │                │                 │                 │                 │
       │                │                 │ ←────────────────┤ Return role    │
       │                │                 │ {id: 'r1',      │ {id: 'r1',     │
       │                │                 │  role_name:     │  role_name:    │
       │                │                 │  'User Admin',  │  'User Admin', │
       │                │                 │  ...}           │  ...}          │
       │                │                 │←────────────────┤                 │
       │                │ ←──────────────→│ Dict returned   │                 │
       │                │                 │                 │                 │
       │                │ (11) CONTROL: Check role match     │                 │
       │                │ if user['role_id'] == role['id']:  │                 │
       │                │ → True ✓                           │                 │
       │                │                 │                 │                 │
       │                │ (12) CONTROL: Generate JWT token   │                 │
       │                │ User.create_session_token(user_id) │                 │
       │                │ (ENTITY operation)                 │                 │
       │                │                 │                 │                 │
       │                │ (13) Generate JWT:                 │                 │
       │                │ payload = {                        │                 │
       │                │   user_id: '123',                  │                 │
       │                │   exp: now + 24h                   │                 │
       │                │ }                                  │                 │
       │                │ token = jwt.encode(...)            │                 │
       │                │ → 'eyJhbGc...'                     │                 │
       │                │ ←──────────────────                │                 │
       │                │                 │ Return JWT token│                 │
       │                │                 │                 │                 │
       │                │ (14) CONTROL: Update last login    │                 │
       │                │ User.update_last_login(user_id)    │                 │
       │                │ (ENTITY operation)                 │                 │
       │                │                 │ ────────────────→│ UPDATE users   │
       │                │                 │                 │ SET last_login │
       │                │                 │                 │ = NOW() WHERE..│
       │                │                 │                 ├──────────────→ │
       │                │                 │                 │ ✓ Updated      │
       │                │                 │                 │←──────────────┤│
       │                │                 │ ←────────────────┤                 │
       │                │                 │ Updated         │                 │
       │                │                 │                 │                 │
       │                │ (15) CONTROL: Get role details     │                 │
       │                │ Role.get_role_by_id(user.role_id)  │                 │
       │                │ (ENTITY operation)                 │                 │
       │                │                 │ ────────────────→│ SELECT * FROM  │
       │                │                 │                 │ roles WHERE...  │
       │                │                 │                 ├──────────────→ │
       │                │                 │                 │ ✓ Found        │
       │                │                 │                 │←──────────────┤│
       │                │                 │ ←────────────────┤ {role details} │
       │                │                 │ Return role dict│                 │
       │                │                 │                 │                 │
       │                │ (16) CONTROL: Return authenticated result
       │                │ return {                           │                 │
       │                │   id: '123',                       │                 │
       │                │   username: 'admin1',              │                 │
       │                │   token: 'eyJhbGc...',             │                 │
       │                │   role: {role_name: 'User Admin'...}
       │                │ }                                  │                 │
       │                │ ←────────────────────────────────┤                 │
       │                │ Result Dict Returned to BOUNDARY   │                 │
       │                │                 │                 │                 │
       │                │ (17) BOUNDARY: Check result        │                 │
       │                │ if result is not None:             │                 │
       │                │ → Success ✓                        │                 │
       │                │                 │                 │                 │
       │                │ (18) BOUNDARY: Format HTTP response│                 │
       │                │ return jsonify({                   │                 │
       │                │   'success': True,                 │                 │
       │                │   'data': {                        │                 │
       │                │     'token': 'eyJhbGc...',         │                 │
       │                │     'user': {...}                  │                 │
       │                │   }                                │                 │
       │                │ }), 200                            │                 │
       │                │                 │                 │                 │
       │ (19) HTTP 200 Response (JSON)    │                 │                 │
       │ {success, token, user}           │                 │                 │
       │←───────────────────────────────┤                 │                 │
       │                │                 │                 │                 │
       │ (20) FRONTEND: Handle response   │                 │                 │
       │ - Extract token: 'eyJhbGc...'   │                 │                 │
       │ - Store in localStorage          │                 │                 │
       │ - Store user info                │                 │                 │
       │ - Redirect to dashboard          │                 │                 │
       │                │                 │                 │                 │

        ✅ LOGIN SUCCESSFUL
```

---

## 2. LOGIN FAILURE SCENARIOS

### Scenario A: Wrong Password

```
Frontend ──POST /api/auth/login──→ AuthController
                                     │
                                     ├─→ User.authenticate_user()
                                     │   │
                                     │   ├─→ User.get_user_by_username() ✓ Found
                                     │   │
                                     │   ├─→ check_password_hash() 
                                     │   │   → False ✗ (wrong password)
                                     │   │
                                     │   └─→ return None
                                     │
                                     ├─ Check result is None
                                     │
                                     └─→ return 401 Unauthorized

Frontend ←─ HTTP 401 (Invalid credentials) ← AuthController
```

---

### Scenario B: User Account Suspended

```
Frontend ──POST /api/auth/login──→ AuthController
                                     │
                                     ├─→ User.authenticate_user()
                                     │   │
                                     │   ├─→ User.get_user_by_username() ✓ Found
                                     │   │
                                     │   ├─→ check_password_hash() ✓ Correct
                                     │   │
                                     │   ├─→ Check user['is_active']
                                     │   │   → False ✗ (account suspended)
                                     │   │
                                     │   └─→ return None
                                     │
                                     └─→ return 401 Unauthorized

Frontend ←─ HTTP 401 (User account suspended) ← AuthController
```

---

### Scenario C: Role Mismatch

```
Frontend ──POST /api/auth/login──→ AuthController
  (role_name: 'CSR')                 │
                                     ├─→ User.authenticate_user()
                                     │   │
                                     │   ├─→ User.get_user_by_username() ✓ Found
                                     │   │   (user is 'User Admin', not 'CSR')
                                     │   │
                                     │   ├─→ check_password_hash() ✓ Correct
                                     │   │
                                     │   ├─→ Check user['is_active'] ✓ True
                                     │   │
                                     │   ├─→ Role.get_role_by_name('CSR') ✓ Found
                                     │   │
                                     │   ├─→ Check user['role_id'] == role['id']
                                     │   │   → False ✗ (role mismatch)
                                     │   │
                                     │   └─→ return None
                                     │
                                     └─→ return 401 Unauthorized

Frontend ←─ HTTP 401 (User role mismatch) ← AuthController
```

---

## 3. LOGOUT FLOW - SEQUENCE DIAGRAM

### Sequence: User logs out and invalidates token

```
┌─────────────┬───────────────────┬─────────────────┬──────────────────┐
│  Frontend   │ AuthController    │ User Entity     │   PostgreSQL     │
│  (Browser)  │  (BOUNDARY)       │  (CONTROL)      │    Database      │
└─────────────┴───────────────────┴─────────────────┴──────────────────┘
       │                │                 │                 │
       │ POST /api/auth/logout             │                 │
       │ Authorization: Bearer <token>    │                 │
       ├───────────────────────────────→│                 │
       │                │                 │                 │
       │                │ (1) Extract Authorization header   │
       │                │ Parse Bearer token: 'eyJhbGc...'   │
       │                │                 │                 │
       │                │ (2) Validate token format          │
       │                │ - Token present? ✓                 │
       │                │ - Bearer prefix? ✓                 │
       │                │                 │                 │
       │                │ (3) Delegate to CONTROL layer      │
       │                │ User.invalidate_session_token(...) │
       │                ├────────────────→│                 │
       │                │                 │                 │
       │                │ (4) CONTROL: Verify token         │
       │                │ - Decode JWT                       │
       │                │ - Check expiration                 │
       │                │ - Get user_id from payload         │
       │                │                 │                 │
       │                │ (5) Add token to blacklist         │
       │                │ (if implemented)                   │
       │                │ INSERT INTO token_blacklist        │
       │                │ (token, user_id, expires_at)       │
       │                │                 │ ────────────────→│
       │                │                 │                 │
       │                │                 │ ✓ Token added   │
       │                │                 │←────────────────┤
       │                │                 │                 │
       │                │ (6) Return success                 │
       │                │ return True                        │
       │                │ ←────────────────────────────────┤
       │                │                 │                 │
       │                │ (7) Format HTTP response           │
       │                │ return jsonify({                   │
       │                │   'success': True,                 │
       │                │   'message': 'Logout successful'    │
       │                │ }), 200                            │
       │                │                 │                 │
       │ HTTP 200 OK                       │                 │
       │←───────────────────────────────┤                 │
       │                │                 │                 │
       │ Delete token from localStorage    │                 │
       │ Clear user session                │                 │
       │ Redirect to login page            │                 │
       │                │                 │                 │

        ✅ LOGOUT SUCCESSFUL
```

---

## 4. TOKEN VERIFICATION - SEQUENCE DIAGRAM

### Sequence: Protected route verifies JWT token

```
┌─────────────┬───────────────────┬─────────────────┬──────────────────┐
│  Frontend   │ AuthController    │ User Entity     │   PostgreSQL     │
│  (Browser)  │  (BOUNDARY)       │  (CONTROL)      │    Database      │
└─────────────┴───────────────────┴─────────────────┴──────────────────┘
       │                │                 │                 │
       │ GET /api/auth/verify              │                 │
       │ Authorization: Bearer <token>    │                 │
       ├───────────────────────────────→│                 │
       │                │                 │                 │
       │                │ (1) Extract Authorization header   │
       │                │ Parse Bearer token: 'eyJhbGc...'   │
       │                │                 │                 │
       │                │ (2) Validate token format          │
       │                │                 │                 │
       │                │ (3) Delegate to CONTROL layer      │
       │                │ User.verify_session_token(token)   │
       │                ├────────────────→│                 │
       │                │                 │                 │
       │                │ (4) CONTROL: Decode & verify JWT   │
       │                │ - Decode payload                   │
       │                │ - Check signature                  │
       │                │ - Check expiration time            │
       │                │ → Signature valid ✓                │
       │                │ → Not expired ✓                    │
       │                │                 │                 │
       │                │ (5) Extract user_id from token     │
       │                │ user_id = 'abc123'                 │
       │                │                 │                 │
       │                │ (6) Check if token blacklisted     │
       │                │ User.is_token_blacklisted(token)   │
       │                │ (ENTITY operation)                 │
       │                │                 │ ────────────────→│
       │                │                 │ SELECT FROM     │
       │                │                 │ token_blacklist │
       │                │                 │ WHERE token=?   │
       │                │                 │ ✓ Not found     │
       │                │                 │←────────────────┤
       │                │ ← Token not blacklisted            │
       │                │                 │                 │
       │                │ (7) Get user details (ENTITY call) │
       │                │ User.get_user_by_id(user_id)       │
       │                │                 │ ────────────────→│
       │                │                 │ SELECT * FROM   │
       │                │                 │ users WHERE id  │
       │                │                 │ ✓ Found         │
       │                │                 │←────────────────┤
       │                │ ←─ Return user dict                │
       │                │                 │                 │
       │                │ (8) Return verification result     │
       │                │ return {                           │
       │                │   verified: True,                  │
       │                │   user_id: 'abc123',               │
       │                │   user: {id, username, role}       │
       │                │ }                                  │
       │                │ ←────────────────────────────────┤
       │                │                 │                 │
       │                │ (9) Format HTTP response           │
       │                │ return jsonify({                   │
       │                │   'success': True,                 │
       │                │   'verified': True,                │
       │                │   'user': {...}                    │
       │                │ }), 200                            │
       │                │                 │                 │
       │ HTTP 200 OK                       │                 │
       │ {verified: true, user: {...}}     │                 │
       │←───────────────────────────────┤                 │
       │                │                 │                 │
       │ Token valid ✓                     │                 │
       │ User can access protected route   │                 │
       │                │                 │                 │

        ✅ VERIFICATION SUCCESSFUL
```

---

## 5. CREATE USER ACCOUNT - SEQUENCE DIAGRAM

### Sequence: Admin creates new user

```
┌─────────────┬─────────────────────────┬─────────────────┬──────────────────┐
│  Frontend   │ CreateUserAccount       │ User Entity     │   PostgreSQL     │
│  (Browser)  │ Controller (BOUNDARY)   │  (CONTROL)      │    Database      │
└─────────────┴─────────────────────────┴─────────────────┴──────────────────┘
       │                     │                 │                 │
       │ POST /api/userAccount                 │                 │
       │ {username, password, email, ...}     │                 │
       ├────────────────────────────────────→│                 │
       │                     │                 │                 │
       │                     │ (1) Extract JSON data            │
       │                     │ - username: 'newuser'            │
       │                     │ - password: 'temppass123'        │
       │                     │ - email: 'newuser@example.com'   │
       │                     │ - full_name: 'New User'          │
       │                     │ - role_id: 'r1'                  │
       │                     │                 │                 │
       │                     │ (2) Validate HTTP format         │
       │                     │ - All fields present? ✓          │
       │                     │ - Valid email? ✓                 │
       │                     │                 │                 │
       │                     │ (3) Delegate to CONTROL layer    │
       │                     │ User.create_user(...)            │
       │                     ├────────────────→│                 │
       │                     │                 │                 │
       │                     │ (4) CONTROL: Check username taken│
       │                     │ User.get_user_by_username(...)   │
       │                     │ (ENTITY operation)               │
       │                     │                 │ ────────────────→│
       │                     │                 │ SELECT * FROM   │
       │                     │                 │ users WHERE     │
       │                     │                 │ username=?      │
       │                     │                 │ ✓ Not found     │
       │                     │                 │←────────────────┤
       │                     │ ← Username not taken ✓            │
       │                     │                 │                 │
       │                     │ (5) CONTROL: Hash password       │
       │                     │ password_hash = generate_password_hash(
       │                     │   'temppass123'                  │
       │                     │ )                                │
       │                     │ → '$2b$12$...'                   │
       │                     │                 │                 │
       │                     │ (6) CONTROL: Verify role exists  │
       │                     │ Role.get_role_by_id('r1')        │
       │                     │ (ENTITY operation)               │
       │                     │                 │ ────────────────→│
       │                     │                 │ SELECT * FROM   │
       │                     │                 │ roles WHERE id  │
       │                     │                 │ ✓ Found         │
       │                     │                 │←────────────────┤
       │                     │ ← Role exists ✓                  │
       │                     │                 │                 │
       │                     │ (7) CONTROL: Verify caller admin │
       │                     │ (Already done by @require_role   │
       │                     │  middleware in BOUNDARY)         │
       │                     │ → Caller is User Admin ✓          │
       │                     │                 │                 │
       │                     │ (8) CONTROL: Insert new user     │
       │                     │ User.create_user_in_db({...})    │
       │                     │ (ENTITY operation)               │
       │                     │                 │ ────────────────→│
       │                     │                 │ INSERT INTO     │
       │                     │                 │ users           │
       │                     │                 │ (username,      │
       │                     │                 │  password_hash, │
       │                     │                 │  email, ...) ✓  │
       │                     │                 │←────────────────┤
       │                     │ ← Return created user dict       │
       │                     │ {id: 'new123', username: ...}    │
       │                     │                 │                 │
       │                     │ (9) CONTROL: Return user         │
       │                     │ return {                         │
       │                     │   id: 'new123',                  │
       │                     │   username: 'newuser',           │
       │                     │   email: 'newuser@example.com',  │
       │                     │   role_id: 'r1'                  │
       │                     │ }                                │
       │                     │ ←────────────────────────────────┤
       │                     │ User created in CONTROL          │
       │                     │                 │                 │
       │                     │ (10) Format HTTP response        │
       │                     │ return jsonify({                 │
       │                     │   'success': True,               │
       │                     │   'message': 'User created',      │
       │                     │   'data': {...}                  │
       │                     │ }), 201                          │
       │                     │                 │                 │
       │ HTTP 201 CREATED                      │                 │
       │ {success, message, data}              │                 │
       │←────────────────────────────────────┤                 │
       │                     │                 │                 │
       │ Display success message               │                 │
       │ Add new user to user list             │                 │
       │                     │                 │                 │

        ✅ USER CREATED SUCCESSFULLY
```

---

## 6. Architecture Flow Summary

### For Every Request

```
1. FRONTEND
   └─ Make HTTP request

2. BOUNDARY (Controller)
   ├─ Extract HTTP data
   ├─ Validate HTTP format
   └─ Delegate to CONTROL

3. CONTROL (Entity static methods)
   ├─ Check business rules
   ├─ Make decisions
   └─ Call ENTITY methods

4. ENTITY (Entity database methods)
   ├─ Execute SQL queries
   └─ Return data

5. BOUNDARY (Controller)
   ├─ Receive result from CONTROL
   ├─ Format HTTP response
   └─ Send to FRONTEND

6. FRONTEND
   └─ Handle response
```

---

## 7. Key Differences from Before

### BEFORE (❌ Incorrect)

```
Frontend
  ↓
AuthController (BOUNDARY)
  ├─ Extract JSON
  ├─ Check password ← WRONG HERE
  ├─ Verify role ← WRONG HERE
  ├─ Generate token ← WRONG HERE
  └─ Format response
  ↓
Database
```

**Problem:** Business logic mixed in BOUNDARY layer

---

### AFTER (✅ Correct)

```
Frontend
  ↓
AuthController (BOUNDARY)
  ├─ Extract JSON
  └─ Delegate to CONTROL
  ↓
User.authenticate_user() (CONTROL)
  ├─ Check password ← CORRECT HERE
  ├─ Verify role ← CORRECT HERE
  ├─ Generate token ← CORRECT HERE
  └─ Call ENTITY methods
  ↓
Entity methods (ENTITY)
  └─ Database operations
  ↓
Database
```

**Benefit:** Clean separation of concerns

---

**Status:** ✅ Complete & Current  
**Aligns with:** October 26, 2025 authentication refactoring  
**Reflects:** Actual request/response flows in refactored system
