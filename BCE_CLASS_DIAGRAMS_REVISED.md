# BCE Class Diagrams - REVISED (Post-Authentication Refactoring)

**Last Updated:** October 26, 2025  
**Status:** Reflects current refactored authentication system

---

## 1. LOGIN FEATURE - REVISED CLASS DIAGRAM

### Complete Class Structure (Authentication Refactored)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BOUNDARY LAYER                                   │
│                   (HTTP Interface Only)                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ LoginPage (Frontend Component)                                   │   │
│  │ Location: src/app/page.js                                        │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - formData: {username, password, role_name}                     │   │
│  │  - error: string | null                                          │   │
│  │  - loading: boolean                                              │   │
│  │  - router: NextRouter                                            │   │
│  │  - axiosInstance: AxiosInstance                                  │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + handleChange(e): void                                         │   │
│  │  + handleSubmit(e): Promise<void>                                │   │
│  │    └─ Calls: POST /api/auth/login                               │   │
│  │  + render(): JSX.Element                                         │   │
│  │                                                                  │   │
│  │ Responsibilities:                                                │   │
│  │  ✓ Render UI form                                               │   │
│  │  ✓ Collect user input                                           │   │
│  │  ✓ Make HTTP request                                            │   │
│  │  ✗ NO business logic                                            │   │
│  │  ✗ NO password verification                                     │   │
│  │  ✗ NO token generation                                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ HTTP POST Request                                           │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ AuthController (Backend - BOUNDARY Layer)                        │   │
│  │ Location: src/controller/auth/auth_controller.py                 │   │
│  │ Type: Flask Blueprint                                            │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - request: Flask.Request                                        │   │
│  │  - jsonify: Flask JSON response formatter                        │   │
│  │  - User: Entity class reference                                  │   │
│  │  - Role: Entity class reference                                  │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + login(request) -> Response                                    │   │
│  │    ├─ Extract JSON data                                         │   │
│  │    ├─ Validate required fields                                  │   │
│  │    ├─ Call User.authenticate_user() ← CONTROL LAYER             │   │
│  │    ├─ Check response                                            │   │
│  │    └─ Format HTTP response (200 or 401)                         │   │
│  │                                                                  │   │
│  │  + logout(request) -> Response                                   │   │
│  │    └─ Delegates to User.invalidate_session_token()             │   │
│  │                                                                  │   │
│  │  + verify(request) -> Response                                   │   │
│  │    └─ Delegates to User.verify_session_token()                 │   │
│  │                                                                  │   │
│  │ Responsibilities:                                                │   │
│  │  ✓ Extract HTTP request data                                    │   │
│  │  ✓ Validate HTTP format (structure)                             │   │
│  │  ✓ Format HTTP responses                                        │   │
│  │  ✓ Return appropriate HTTP status codes                         │   │
│  │  ✗ NO password verification ← Moved to CONTROL                 │   │
│  │  ✗ NO role verification ← Moved to CONTROL                     │   │
│  │  ✗ NO token generation ← Moved to CONTROL                      │   │
│  │  ✗ NO business logic                                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓↓↓
                    Delegates to CONTROL Layer
                              ↓↓↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     CONTROL LAYER                                        │
│              (Business Logic - Static Methods)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ User.authenticate_user() ✨ NEW                                  │   │
│  │ Location: src/entity/user.py                                     │   │
│  │ Type: @staticmethod (CONTROL Layer Logic)                        │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Signature:                                                       │   │
│  │  authenticate_user(username: str, password: str,                │   │
│  │                    role_name: str) -> Optional[Dict]            │   │
│  │                                                                  │   │
│  │ Implementation Steps:                                            │   │
│  │  1. Get user by username (calls ENTITY)                         │   │
│  │     └─ User.get_user_by_username(username)                      │   │
│  │                                                                  │   │
│  │  2. Verify password (business rule)                             │   │
│  │     └─ check_password_hash(password, user['password_hash'])     │   │
│  │                                                                  │   │
│  │  3. Check user active (business rule)                           │   │
│  │     └─ if not user['is_active']: return None                    │   │
│  │                                                                  │   │
│  │  4. Verify role (business rule)                                 │   │
│  │     ├─ Role.get_role_by_name(role_name) (ENTITY)                │   │
│  │     └─ Check user['role_id'] == role['id']                      │   │
│  │                                                                  │   │
│  │  5. Generate token (business operation)                         │   │
│  │     └─ User.create_session_token(user_id) (ENTITY)              │   │
│  │                                                                  │   │
│  │  6. Update last login (business operation)                      │   │
│  │     └─ User.update_last_login(user_id) (ENTITY)                 │   │
│  │                                                                  │   │
│  │  7. Get role details (ENTITY)                                   │   │
│  │     └─ Role.get_role_by_id(role_id)                             │   │
│  │                                                                  │   │
│  │  8. Return authenticated response                               │   │
│  │     └─ {id, username, token, role, email, full_name}            │   │
│  │                                                                  │   │
│  │ Returns: Dict (success) | None (failure)                        │   │
│  │                                                                  │   │
│  │ Responsibilities:                                                │   │
│  │  ✓ Implement authentication business rules                      │   │
│  │  ✓ Verify password                                              │   │
│  │  ✓ Verify user status                                           │   │
│  │  ✓ Verify role assignment                                       │   │
│  │  ✓ Generate JWT token                                           │   │
│  │  ✓ Update last login timestamp                                  │   │
│  │  ✓ Call ENTITY methods for operations                           │   │
│  │  ✗ NO HTTP handling                                             │   │
│  │  ✗ NO direct database queries                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Calls ENTITY Methods                                        │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Other CONTROL Methods (Orchestration)                           │   │
│  │ Location: src/entity/user.py                                     │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │ User.invalidate_session_token(token: str) -> bool              │   │
│  │  Purpose: Invalidate JWT token (logout)                        │   │
│  │                                                                  │   │
│  │ User.verify_session_token(token: str) -> Optional[Dict]        │   │
│  │  Purpose: Verify JWT token validity                            │   │
│  │                                                                  │   │
│  │ Role.verify_user_role(user_id: str, role_id: str) -> bool      │   │
│  │  Purpose: Verify user has required role                        │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓↓↓
                    Calls ENTITY Layer Methods
                              ↓↓↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      ENTITY LAYER                                        │
│          (Database Operations - Static Methods)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ User (Entity Class)                                              │   │
│  │ Location: src/entity/user.py                                     │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Database Operations:                                             │   │
│  │                                                                  │   │
│  │  + get_user_by_username(username: str) -> Optional[Dict]        │   │
│  │    └─ SQL: SELECT * FROM users WHERE username = ?               │   │
│  │                                                                  │   │
│  │  + get_user_by_id(user_id: str) -> Optional[Dict]               │   │
│  │    └─ SQL: SELECT * FROM users WHERE id = ?                     │   │
│  │                                                                  │   │
│  │  + create_session_token(user_id: str) -> str                    │   │
│  │    └─ Generate JWT token with payload {user_id, exp}            │   │
│  │                                                                  │   │
│  │  + update_last_login(user_id: str) -> bool                      │   │
│  │    └─ SQL: UPDATE users SET last_login = NOW() WHERE id = ?     │   │
│  │                                                                  │   │
│  │  + verify_password(password: str, hash: str) -> bool            │   │
│  │    └─ check_password_hash(password, hash)                       │   │
│  │                                                                  │   │
│  │  + invalidate_session_token(token: str) -> bool                 │   │
│  │    └─ Add token to blacklist (if implemented) or just return    │   │
│  │                                                                  │   │
│  │  + verify_session_token(token: str) -> Optional[Dict]           │   │
│  │    └─ Decode JWT and verify validity                            │   │
│  │                                                                  │   │
│  │ Responsibilities:                                                │   │
│  │  ✓ Execute database queries                                     │   │
│  │  ✓ Generate/verify JWT tokens                                   │   │
│  │  ✓ Return domain objects (Dict)                                 │   │
│  │  ✗ NO business logic decisions                                  │   │
│  │  ✗ NO HTTP handling                                             │   │
│  │  ✗ NO authentication logic (CONTROL handles this)              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Calls                                                        │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Role (Entity Class)                                              │   │
│  │ Location: src/entity/role.py                                     │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  + get_role_by_id(role_id: str) -> Optional[Dict]               │   │
│  │    └─ SQL: SELECT * FROM roles WHERE id = ?                     │   │
│  │                                                                  │   │
│  │  + get_role_by_name(role_name: str) -> Optional[Dict]           │   │
│  │    └─ SQL: SELECT * FROM roles WHERE role_name = ?              │   │
│  │                                                                  │   │
│  │  + verify_role_exists(role_id: str) -> bool                     │   │
│  │    └─ SQL: SELECT * FROM roles WHERE id = ? LIMIT 1             │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓↓↓
                         SQL Queries
                              ↓↓↓
          ┌────────────────────────────────────────┐
          │   PostgreSQL Database (Supabase)       │
          │                                        │
          │ Tables:                                │
          │  - users (id, username, password_hash,│
          │           email, full_name, role_id,  │
          │           is_active, last_login, ...)│
          │                                        │
          │  - roles (id, role_name, role_code,   │
          │           dashboard_route, ...)       │
          │                                        │
          └────────────────────────────────────────┘
```

---

## 2. Key Difference: Before vs After Authentication Refactoring

### BEFORE (❌ Incorrect - Mixed Concerns)

```
BOUNDARY (AuthController):
├─ Extract JSON
├─ Validate fields
├─ ❌ Check password ← WRONG LAYER
├─ ❌ Verify role ← WRONG LAYER
├─ ❌ Generate token ← WRONG LAYER
├─ Format response
└─ Return HTTP status

    ↓ (calls directly)

ENTITY:
├─ get_user_by_username()
├─ get_role_by_name()
└─ (all database operations)
```

**Problems:**
- Controller contains business logic
- Hard to test business logic without HTTP
- Can't reuse authentication logic elsewhere
- Violates BCE architecture

---

### AFTER (✅ Correct - Clean Separation)

```
BOUNDARY (AuthController):
├─ Extract JSON
├─ Validate fields
├─ Delegate to User.authenticate_user()
├─ Check response
├─ Format response
└─ Return HTTP status

    ↓

CONTROL (User.authenticate_user):
├─ Get user (call ENTITY)
├─ ✅ Check password ← CORRECT LAYER
├─ ✅ Check active status ← CORRECT LAYER
├─ ✅ Verify role ← CORRECT LAYER
├─ ✅ Generate token ← CORRECT LAYER
├─ ✅ Update last_login ← CORRECT LAYER
└─ Return {user, role, token}

    ↓

ENTITY:
├─ get_user_by_username()
├─ get_role_by_name()
├─ create_session_token()
├─ update_last_login()
└─ (all database operations)
```

**Advantages:**
- Clear separation of concerns
- Business logic testable independently
- Authentication logic reusable
- Follows BCE architecture principles

---

## 3. USER ADMIN FEATURE - CLASS DIAGRAM

### Create User Account

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BOUNDARY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ CreateUserAccountController                                      │   │
│  │ Location: src/controller/userAccount/                            │   │
│  │           create_user_account_controller.py                      │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ POST /api/userAccount                                            │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + create(request) -> Response                                   │   │
│  │    ├─ Extract JSON: username, password, email, full_name       │   │
│  │    ├─ Validate required fields                                  │   │
│  │    ├─ Call User.create_user() ← CONTROL LAYER                  │   │
│  │    ├─ Check response                                            │   │
│  │    └─ Return 201 or 400                                         │   │
│  │                                                                  │   │
│  │ Responsibilities:                                                │   │
│  │  ✓ Extract HTTP data                                            │   │
│  │  ✓ Validate HTTP format                                         │   │
│  │  ✓ Format HTTP response                                         │   │
│  │  ✗ NO business logic                                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Delegates to CONTROL                                        │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ User.create_user() - CONTROL LAYER                              │   │
│  │ Location: src/entity/user.py                                     │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  @staticmethod                                                  │   │
│  │  create_user(username, password, email, full_name,              │   │
│  │             role_id) -> Optional[Dict]                          │   │
│  │                                                                  │   │
│  │  Steps:                                                          │   │
│  │  1. Check username not taken (ENTITY call)                      │   │
│  │  2. Hash password                                               │   │
│  │  3. Verify role exists (ENTITY call)                            │   │
│  │  4. Verify caller is admin (business rule)                      │   │
│  │  5. Call ENTITY to insert user                                  │   │
│  │  6. Return created user dict                                    │   │
│  │                                                                  │   │
│  │ Responsibilities:                                                │   │
│  │  ✓ Implement business rules                                     │   │
│  │  ✓ Call ENTITY methods                                          │   │
│  │  ✗ NO HTTP handling                                             │   │
│  │  ✗ NO direct database queries                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Calls ENTITY                                                │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ ENTITY Layer Operations                                          │   │
│  │                                                                  │   │
│  │  + User.get_user_by_username(username) -> Optional[Dict]        │   │
│  │    └─ SQL: SELECT * FROM users WHERE username = ?               │   │
│  │                                                                  │   │
│  │  + User.create_user_in_db(data: Dict) -> Dict                   │   │
│  │    └─ SQL: INSERT INTO users (...) VALUES (...)                 │   │
│  │                                                                  │   │
│  │  + Role.get_role_by_id(role_id) -> Optional[Dict]               │   │
│  │    └─ SQL: SELECT * FROM roles WHERE id = ?                     │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ SQL Queries                                                 │
│           ↓                                                              │
│      ┌──────────────────┐                                               │
│      │  PostgreSQL DB   │                                               │
│      │   (Supabase)     │                                               │
│      └──────────────────┘                                               │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Architecture Patterns Used

### Pattern 1: **Static Methods for Business Logic**

In Python/Flask with BCE architecture, use static methods in Entity classes for CONTROL layer:

```python
class User:
    # CONTROL Layer - Business Logic
    @staticmethod
    def authenticate_user(username, password, role_name):
        # Business logic here
        pass
    
    # ENTITY Layer - Database Operations
    @staticmethod
    def get_user_by_username(username):
        # SQL query here
        pass
```

### Pattern 2: **Delegation in Controllers**

In Flask controllers, delegate to CONTROL layer:

```python
@auth_blueprint.route('/api/auth/login', methods=['POST'])
def login():
    # BOUNDARY: Extract and validate HTTP
    data = request.get_json()
    validate_input(data)
    
    # CONTROL: Call business logic
    result = User.authenticate_user(...)
    
    # BOUNDARY: Format HTTP response
    return jsonify(...), status
```

### Pattern 3: **Responsibility Flow**

```
Frontend → BOUNDARY (HTTP) → CONTROL (Business) → ENTITY (Database) → DB
```

Each layer has clear responsibilities, no crossing over.

---

## 5. Class Interaction Diagram

```
┌────────────────────┐
│   LoginPage        │
│   (Frontend)       │
└────────────────────┘
         │ HTTP POST
         ↓
┌────────────────────┐
│  AuthController    │
│  (BOUNDARY)        │
└────────────────────┘
         │ Method Call
         ↓
┌────────────────────┐
│ User.              │
│ authenticate_user()│
│ (CONTROL)          │
└────────────────────┘
    │         │         │
    │         │         └────────────┐
    │         │                      │
    ↓         ↓                      ↓
┌─────────┐ ┌───────────┐  ┌──────────────────┐
│ User    │ │ Role      │  │ User             │
│.get_    │ │.get_role_ │  │.create_session_  │
│user_by_ │ │by_name()  │  │token()           │
│username │ │ (ENTITY)  │  │ (ENTITY)         │
│(ENTITY) │ └───────────┘  └──────────────────┘
└─────────┘
    │           │               │
    └───────┬───┴───────────────┘
            │
            ↓
      ┌──────────────┐
      │  PostgreSQL  │
      │   Database   │
      └──────────────┘
```

---

## 6. Summary Table: What Goes Where

| Operation | Layer | Class/File |
|-----------|-------|-----------|
| Render login form | BOUNDARY | LoginPage (src/app/page.js) |
| Extract username/password | BOUNDARY | AuthController |
| Validate required fields | BOUNDARY | AuthController |
| **Verify password** | **CONTROL** | **User.authenticate_user()** |
| **Check user active** | **CONTROL** | **User.authenticate_user()** |
| **Verify role assignment** | **CONTROL** | **User.authenticate_user()** |
| **Generate JWT token** | **CONTROL** | **User.authenticate_user()** |
| **Update last_login** | **CONTROL** | **User.authenticate_user()** |
| Format HTTP response | BOUNDARY | AuthController |
| Query users table | ENTITY | User.get_user_by_username() |
| Query roles table | ENTITY | Role.get_role_by_name() |
| Generate token bytes | ENTITY | User.create_session_token() |
| Update database | ENTITY | User.update_last_login() |

---

**Status:** ✅ Complete & Current  
**Aligns with:** October 26, 2025 authentication refactoring  
**Reflects:** Actual code structure and layer responsibilities
