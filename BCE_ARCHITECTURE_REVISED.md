# BCE Architecture - Revised (Post-Authentication Refactoring)

**Last Updated:** October 26, 2025  
**Reason for Revision:** Authentication logic moved to CONTROL layer per lecturer guidance

---

## 1. Architecture Overview

The CSR Application uses **Boundary-Control-Entity (BCE)** three-layer architecture:

```
┌──────────────────────────────────────────────────────────────────────┐
│                     PRESENTATION (Frontend)                           │
│                    Next.js React Application                          │
│              (src/app/page.js, src/app/*/page.js)                    │
│                                                                       │
│  Responsibilities:                                                    │
│  ✓ Render UI components                                              │
│  ✓ Collect user input                                                │
│  ✓ Make HTTP requests to API                                         │
│  ✓ Store JWT tokens in localStorage                                  │
│  ✓ Handle client-side routing                                        │
│  ✗ NO business logic                                                 │
│  ✗ NO database queries                                               │
└──────────────────────────────────────────────────────────────────────┘
                              ↕ HTTP
                    (REST API Calls via Axios)
┌──────────────────────────────────────────────────────────────────────┐
│                    BOUNDARY LAYER (HTTP Interface)                   │
│                 Flask Controllers/Blueprints                          │
│        (src/controller/*/\*_controller.py)                           │
│                                                                       │
│  Responsibilities:                                                    │
│  ✓ Listen for HTTP requests                                          │
│  ✓ Extract data from request body/params/headers                     │
│  ✓ Validate HTTP input format (structure)                            │
│  ✓ Call CONTROL layer methods                                        │
│  ✓ Format HTTP responses                                             │
│  ✓ Return appropriate HTTP status codes                              │
│  ✗ NO business logic                                                 │
│  ✗ NO database queries directly                                      │
│  ✗ NO decision-making about business rules                           │
└──────────────────────────────────────────────────────────────────────┘
                         ↕ Method Calls
                     (Direct Python Calls)
┌──────────────────────────────────────────────────────────────────────┐
│                  CONTROL LAYER (Business Logic)                      │
│                 Static Methods in Entity Classes                      │
│        (src/entity/user.py, src/entity/role.py, etc.)               │
│                                                                       │
│  Responsibilities:                                                    │
│  ✓ Implement business rules                                          │
│  ✓ Validate business logic                                           │
│  ✓ Authenticate and authorize users                                  │
│  ✓ Generate and manage JWT tokens                                    │
│  ✓ Orchestrate operations across multiple entities                   │
│  ✓ Update timestamps (created_at, last_login, etc.)                  │
│  ✓ Call ENTITY layer methods                                         │
│  ✗ NO HTTP handling                                                  │
│  ✗ NO direct database queries                                        │
│  ✗ NO response formatting                                            │
└──────────────────────────────────────────────────────────────────────┘
                         ↕ Method Calls
                     (Direct Python Calls)
┌──────────────────────────────────────────────────────────────────────┐
│                   ENTITY LAYER (Data Persistence)                    │
│                  Database Operation Classes                           │
│        (src/entity/user.py, src/entity/role.py, etc.)               │
│                                                                       │
│  Responsibilities:                                                    │
│  ✓ Execute database queries (SELECT, INSERT, UPDATE, DELETE)         │
│  ✓ Retrieve data from PostgreSQL                                     │
│  ✓ Return domain objects/dictionaries                                │
│  ✓ Handle database connections                                       │
│  ✗ NO business logic decisions                                       │
│  ✗ NO HTTP handling                                                  │
│  ✗ NO authentication logic                                           │
└──────────────────────────────────────────────────────────────────────┘
                              ↕ SQL
                    (Database Queries via Supabase)
┌──────────────────────────────────────────────────────────────────────┐
│                         DATABASE (PostgreSQL)                         │
│                    Supabase Cloud Database                            │
│                                                                       │
│  Tables:                                                              │
│  - users                                                              │
│  - roles                                                              │
│  - user_profiles                                                      │
│  - csr_requests                                                       │
│  - (and other domain tables)                                          │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Key Principle: Separation of Concerns

### ✅ CORRECT - After Refactoring

```
User Login Flow:

1. FRONTEND (Next.js):
   - Render form
   - Collect: username, password, role_name
   - POST to /api/auth/login
   
   ↓

2. BOUNDARY (AuthController):
   - Extract JSON from request
   - Validate required fields
   - Call User.authenticate_user() ← Delegates business logic
   - Format HTTP response
   - Return 200 (success) or 401 (failure)

   ↓

3. CONTROL (User.authenticate_user):
   - Get user by username (call ENTITY)
   - Check password hash
   - Check user is active
   - Verify role assignment
   - Generate JWT token (call ENTITY)
   - Update last_login (call ENTITY)
   - Get role details (call ENTITY)
   - Return {user, role, token} dict

   ↓

4. ENTITY (User static methods):
   - User.get_user_by_username(username) → DB query
   - User.create_session_token(user_id) → Generate JWT
   - User.update_last_login(user_id) → DB update
   - Role.get_role_by_name(role_name) → DB query
   - Role.get_role_by_id(role_id) → DB query

   ↓

5. DATABASE (PostgreSQL):
   - SELECT * FROM users WHERE username = ?
   - UPDATE users SET last_login = ? WHERE id = ?
   - SELECT * FROM roles WHERE id = ?
```

### ❌ INCORRECT - Before Refactoring

```
Was doing authentication in BOUNDARY (AuthController):
- Extract JSON
- Check password directly ❌ Business logic
- Verify role exists ❌ Business logic
- Create JWT token ❌ Business logic
- Format response
- Return status
```

---

## 3. Layer Responsibilities

### BOUNDARY Layer (HTTP Interface)

**Location:** `src/controller/auth/auth_controller.py`

**Responsibility:** Handle HTTP requests and responses ONLY

**What it DOES:**
```python
@auth_blueprint.route('/api/auth/login', methods=['POST'])
def login():
    # 1. Extract HTTP data
    data = request.get_json()
    
    # 2. Validate HTTP structure
    if not data or 'username' not in data:
        return jsonify({'success': False}), 400
    
    # 3. Call CONTROL layer
    result = User.authenticate_user(
        username=data['username'],
        password=data['password'],
        role_name=data['role_name']
    )
    
    # 4. Format HTTP response
    if result:
        return jsonify({'success': True, 'token': result['token']}), 200
    else:
        return jsonify({'success': False}), 401
```

**What it does NOT do:**
- ❌ Check passwords
- ❌ Verify roles
- ❌ Generate tokens
- ❌ Query database
- ❌ Make decisions about business rules

---

### CONTROL Layer (Business Logic)

**Location:** `src/entity/user.py` (static methods)

**Responsibility:** Implement business rules and orchestrate operations

**What it DOES:**
```python
@staticmethod
def authenticate_user(username: str, password: str, role_name: str) -> Optional[Dict]:
    """
    CONTROL layer: Complete authentication orchestration
    
    This method implements the business rule:
    "A user can login if their password is correct, 
     their account is active, and their role matches the selection"
    """
    
    # 1. Get user from database (ENTITY call)
    user = User.get_user_by_username(username)
    if not user:
        return None  # Business rule: user must exist
    
    # 2. Check password (CONTROL logic: business rule)
    if not check_password_hash(user['password_hash'], password):
        return None  # Business rule: password must match
    
    # 3. Check active status (CONTROL logic: business rule)
    if not user['is_active']:
        return None  # Business rule: user account must be active
    
    # 4. Verify role (CONTROL logic: business rule)
    role = Role.get_role_by_name(role_name)
    if not role or user['role_id'] != role['id']:
        return None  # Business rule: user's role must match selection
    
    # 5. Generate token (CONTROL operation)
    token = User.create_session_token(user['id'])
    
    # 6. Update last login (CONTROL operation)
    User.update_last_login(user['id'])
    
    # 7. Get role details (ENTITY call)
    role_details = Role.get_role_by_id(user['role_id'])
    
    # 8. Return business decision (CONTROL responsibility)
    return {
        'id': user['id'],
        'username': user['username'],
        'token': token,
        'role': role_details
    }
```

**What it does NOT do:**
- ❌ Handle HTTP requests
- ❌ Format HTTP responses
- ❌ Return HTTP status codes
- ❌ Query database directly (delegates to ENTITY)

---

### ENTITY Layer (Data Persistence)

**Location:** `src/entity/user.py` (database methods)

**Responsibility:** Database operations ONLY

**What it DOES:**
```python
class User:
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """ENTITY: Direct database query"""
        supabase = get_supabase()
        response = supabase.table('users').select('*').eq('username', username).execute()
        return response.data[0] if response.data else None
    
    @staticmethod
    def create_session_token(user_id: str) -> str:
        """ENTITY: Generate and store JWT token"""
        payload = {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=24)}
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return token
    
    @staticmethod
    def update_last_login(user_id: str) -> bool:
        """ENTITY: Update database timestamp"""
        supabase = get_supabase()
        supabase.table('users').update({'last_login': datetime.utcnow()}).eq('id', user_id).execute()
        return True
```

**What it does NOT do:**
- ❌ Check business logic
- ❌ Make authentication decisions
- ❌ Handle HTTP
- ❌ Validate business rules

---

## 4. Data Flow Diagram: Complete Login Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (Next.js - src/app/page.js)                            │
│                                                                  │
│ 1. User enters: username, password, role_name                  │
│ 2. Click "Login" button                                         │
│ 3. axios.post('/api/auth/login', {                             │
│      username: 'admin1',                                        │
│      password: 'pass123',                                       │
│      role_name: 'User Admin'                                    │
│    })                                                            │
└─────────────────────────────────────────────────────────────────┘
                           ↓ HTTP POST
                  HTTP Request Sent to Backend
┌─────────────────────────────────────────────────────────────────┐
│ BOUNDARY (Flask - auth_controller.py)                           │
│                                                                  │
│ @auth_blueprint.route('/api/auth/login', methods=['POST'])     │
│                                                                  │
│ 1. Extract JSON:                                               │
│    - username: 'admin1'                                         │
│    - password: 'pass123'                                        │
│    - role_name: 'User Admin'                                    │
│                                                                  │
│ 2. Validate structure:                                          │
│    - Check all fields present? ✓                                │
│    - Check data types? ✓                                        │
│    (This is HTTP validation, not business validation)          │
│                                                                  │
│ 3. Delegate to CONTROL layer:                                  │
│    result = User.authenticate_user(                             │
│      'admin1', 'pass123', 'User Admin'                          │
│    )                                                             │
└─────────────────────────────────────────────────────────────────┘
                      ↓ Python Method Call
                   CONTROL Logic Execution
┌─────────────────────────────────────────────────────────────────┐
│ CONTROL (User.authenticate_user - user.py)                     │
│                                                                  │
│ 1. Get user from database:                                     │
│    user = User.get_user_by_username('admin1')                  │
│    → Call ENTITY layer                                         │
│    ← Returns: {id: '123', username: 'admin1', password_hash:   │
│              '...', is_active: true, role_id: 'r1', ...}       │
│                                                                  │
│ 2. Check password:                                              │
│    check_password_hash('pass123', user['password_hash'])       │
│    → True ✓                                                     │
│                                                                  │
│ 3. Check user active:                                           │
│    user['is_active'] → True ✓                                   │
│                                                                  │
│ 4. Verify role:                                                 │
│    role = Role.get_role_by_name('User Admin')                  │
│    → Call ENTITY layer                                         │
│    ← Returns: {id: 'r1', role_name: 'User Admin', ...}         │
│    user['role_id'] == role['id'] → True ✓                      │
│                                                                  │
│ 5. Generate token:                                              │
│    token = User.create_session_token('123')                    │
│    → Call ENTITY layer                                         │
│    ← Returns: 'eyJhbGc...[JWT token]...'                       │
│                                                                  │
│ 6. Update last login:                                           │
│    User.update_last_login('123')                               │
│    → Call ENTITY layer                                         │
│    ← Updates database                                          │
│                                                                  │
│ 7. Get role details:                                            │
│    role_details = Role.get_role_by_id('r1')                   │
│    → Call ENTITY layer                                         │
│    ← Returns: {role_name: 'User Admin', dashboard_route: ...}  │
│                                                                  │
│ 8. Return authenticated response:                              │
│    return {                                                     │
│      'id': '123',                                               │
│      'username': 'admin1',                                      │
│      'token': 'eyJhbGc...',                                     │
│      'role': {role_name: 'User Admin', ...}                     │
│    }                                                             │
└─────────────────────────────────────────────────────────────────┘
                      ↓ Python Return Value
                   Response Returned to BOUNDARY
┌─────────────────────────────────────────────────────────────────┐
│ BOUNDARY (Flask - auth_controller.py)                           │
│                                                                  │
│ 1. Check result from CONTROL:                                  │
│    if not result: return 401 ✗                                  │
│    (result exists, so continue)                                │
│                                                                  │
│ 2. Format HTTP response:                                        │
│    return jsonify({                                             │
│      'success': True,                                           │
│      'message': 'Login successful',                             │
│      'data': {                                                  │
│        'token': 'eyJhbGc...',                                   │
│        'user': {                                                │
│          'id': '123',                                           │
│          'username': 'admin1',                                  │
│          'role': {name: 'User Admin', ...}                      │
│        }                                                         │
│      }                                                           │
│    }), 200                                                       │
└─────────────────────────────────────────────────────────────────┘
                      ↓ HTTP Response
                 HTTP 200 Response Sent
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND (Next.js - src/app/page.js)                            │
│                                                                  │
│ 1. Receive HTTP response:                                       │
│    {                                                             │
│      success: true,                                             │
│      data: {                                                    │
│        token: 'eyJhbGc...',                                     │
│        user: {id: '123', ...}                                   │
│      }                                                           │
│    }                                                             │
│                                                                  │
│ 2. Store token in localStorage:                                │
│    localStorage.setItem('token', 'eyJhbGc...')                │
│                                                                  │
│ 3. Store user info:                                             │
│    localStorage.setItem('user', JSON.stringify({...}))         │
│                                                                  │
│ 4. Redirect to dashboard:                                       │
│    router.push('/admin')  (or '/csr', '/platform' based on      │
│                            user['role'])                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Other Features - Layer Breakdown

### Create User Account

```
FRONTEND:
  - Display form with fields: username, password, email, full_name, role_id
  - POST /api/userAccount
  
    ↓
    
BOUNDARY (createUserAccountController):
  - Extract: username, password, email, full_name, role_id from request
  - Validate: all fields present
  - Call: User.create_user(...)
  - Format response with new user data
  - Return 201 (Created) or 400 (Error)
  
    ↓
    
CONTROL (User.create_user):
  - Check username not taken (call ENTITY)
  - Hash password
  - Verify role exists (call ENTITY)
  - Verify user is admin (business rule)
  - Call ENTITY to insert user
  - Return created user dict
  
    ↓
    
ENTITY:
  - INSERT INTO users (username, password_hash, email, full_name, role_id, ...)
  - SELECT * FROM roles WHERE id = ?
  - Return user dict with inserted ID
```

---

## 6. Summary: Layer Responsibilities

| Operation | BOUNDARY | CONTROL | ENTITY |
|-----------|----------|---------|--------|
| Extract HTTP data | ✅ | ❌ | ❌ |
| Validate HTTP format | ✅ | ❌ | ❌ |
| Format HTTP response | ✅ | ❌ | ❌ |
| Return HTTP status | ✅ | ❌ | ❌ |
| **Authentication** | ❌ | ✅ | ❌ |
| **Password verification** | ❌ | ✅ | ❌ |
| **Role verification** | ❌ | ✅ | ❌ |
| **Token generation** | ❌ | ✅ | ❌ |
| **Business logic** | ❌ | ✅ | ❌ |
| Database queries | ❌ | ❌ | ✅ |
| Data persistence | ❌ | ❌ | ✅ |
| Return domain objects | ❌ | ❌ | ✅ |

---

## 7. Why This Architecture?

### ✅ Advantages

1. **Testability:** Each layer can be tested independently
   - Test CONTROL without HTTP
   - Test BOUNDARY without business logic
   - Test ENTITY without controllers

2. **Reusability:** CONTROL logic can be used from multiple sources
   - REST API, GraphQL, CLI, etc. all use same business logic

3. **Maintainability:** Changes in one layer don't affect others
   - Change database? Update ENTITY only
   - Change HTTP format? Update BOUNDARY only
   - Change rules? Update CONTROL only

4. **Scalability:** Easy to add features
   - New endpoints: create new BOUNDARY files
   - New business logic: extend CONTROL
   - New data: extend ENTITY

5. **Security:** Separation reduces attack surface
   - HTTP layer isolated from business logic
   - Authentication centralized in CONTROL

6. **Industry Standard:** Used by most enterprise applications
   - Recommended by design patterns (Clean Architecture, Hexagonal)
   - Aligns with lecturer expectations

---

## 8. When to Update This Document

Revise this architecture guide when:
- New layers are added
- Layer responsibilities change
- Major business logic is introduced
- New design patterns are implemented
- Lecturer provides feedback on architecture

**Next Review Date:** As needed

---

**Status:** ✅ Complete & Current  
**Aligns with:** Lecturer guidance on JWT token management in CONTROL layer  
**Implements:** Clean Architecture + Boundary-Control-Entity pattern
