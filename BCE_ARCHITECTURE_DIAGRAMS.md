# BCE Architecture: Visual Diagrams

## Quick Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                         │
│                   (Frontend at :3000)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                    HTTP Requests
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              BOUNDARY LAYER (Controllers)                   │
│                                                             │
│  ✓ Validate HTTP input                                     │
│  ✓ Check authentication/authorization                      │
│  ✓ Parse request parameters                                │
│  ✓ Call business logic                                     │
│  ✓ Format JSON response                                    │
│                                                             │
│  Example: @route '/<id>/suspend', methods=['PUT']         │
│           → Validates ID parameter                         │
│           → Calls User.update_user(id, {is_active: false}) │
│           → Returns {success: true, data: {...}}           │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Python Objects
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              CONTROL LAYER (Business Logic)                │
│                                                             │
│  ✓ Enforce business rules                                  │
│  ✓ Validate data relationships                             │
│  ✓ Hash passwords                                          │
│  ✓ Check uniqueness constraints                            │
│  ✓ Verify foreign keys                                     │
│  ✓ Orchestrate operations                                  │
│                                                             │
│  Example: User.update_user(id, {'is_active': False})      │
│           ├─ Verify user exists                            │
│           ├─ If changing email → check unique              │
│           ├─ If changing role → verify role exists         │
│           └─ Call entity layer to persist                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Database Objects
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              ENTITY LAYER (Persistence)                    │
│                                                             │
│  ✓ Execute database queries                                │
│  ✓ Handle Supabase operations                              │
│  ✓ Return database results                                 │
│  ✓ Manage database connections                             │
│                                                             │
│  Example: supabase.table('users')                          │
│           .update({'is_active': False})                    │
│           .eq('id', user_id)                               │
│           .execute()                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                    SQL Queries
                         ↓
┌─────────────────────────────────────────────────────────────┐
│          DATABASE (Supabase PostgreSQL)                    │
│                                                             │
│  Tables: users, roles, profiles, requests                  │
│  Constraints: CASCADE DELETE, foreign keys, indexes         │
└─────────────────────────────────────────────────────────────┘
```

## CREATE USER Use Case

```
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
│ User clicks "Add New User"                                   │
│ Form: username, email, password, full_name, role_id         │
└─────────────────────────────┬────────────────────────────────┘
                              │
                    axios.post('/api/userAccount', {...})
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ BOUNDARY: create_user_account_controller.py                  │
│                                                              │
│ @route.route('/', methods=['POST'])                         │
│ @require_role(Role.USER_ADMIN)                              │
│ def create():                                               │
│     data = request.json  ← Extract request                 │
│     validate(data)  ← Check all required fields            │
│     User.create_user(...)  ← Call Control layer            │
│     return 201 Created ← Return HTTP response              │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ CONTROL: src/entity/user.py - User.create_user()           │
│                                                              │
│ ✓ Rule 1: Check username is unique                         │
│   if User.get_user_by_username(username) exists:           │
│       raise ValueError("Username exists")                   │
│                                                              │
│ ✓ Rule 2: Check email is unique                            │
│   if email exists in database:                             │
│       raise ValueError("Email exists")                      │
│                                                              │
│ ✓ Rule 3: Hash the password                                │
│   hashed = generate_password_hash(password)                │
│                                                              │
│ ✓ Rule 4: Verify role exists                               │
│   if not Role.get_role_by_id(role_id):                     │
│       raise ValueError("Role not found")                    │
│                                                              │
│ ✓ All rules passed → Call Entity layer                     │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ ENTITY: Database Operations                                 │
│                                                              │
│ supabase.table('users').insert({                           │
│     'username': username,                                   │
│     'password': hashed_password,                            │
│     'email': email,                                         │
│     'full_name': full_name,                                 │
│     'role_id': role_id,                                     │
│     'is_active': True,                                      │
│     'created_at': now()                                     │
│ }).execute()                                               │
│                                                              │
│ Database INSERT SQL generated:                             │
│ INSERT INTO users (username, password, email, ...)         │
│ VALUES ('newuser', '$2b$12$hash...', 'email@...', ...)     │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ DATABASE (Supabase)                                          │
│                                                              │
│ NEW USER INSERTED INTO users TABLE:                        │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ id  │ username │ email    │ password   │ role_id │ ... │ │
│ ├─────┼──────────┼──────────┼────────────┼─────────┼─────┤ │
│ │ 5   │ newuser  │ new@...  │ $2b$12... │ 1       │ ... │ │
│ └────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬────────────────────────────────┘
                              │
                         Returns new user object
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ BOUNDARY: Format Response                                   │
│                                                              │
│ return jsonify({                                            │
│     'success': True,                                        │
│     'data': {                                               │
│         'id': 5,                                            │
│         'username': 'newuser',                              │
│         'email': 'new@...',                                 │
│         'full_name': 'New User',                            │
│         'role_id': 1,                                       │
│         'is_active': True                                   │
│     },                                                      │
│     'message': 'User created successfully'                  │
│ }), 201  ← HTTP 201 Created Status                         │
└─────────────────────────────┬────────────────────────────────┘
                              │
                    HTTP Response with JSON
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
│ Receives response and:                                       │
│ ✓ Shows success message                                     │
│ ✓ Updates user table                                        │
│ ✓ Closes form modal                                         │
│ ✓ Refreshes user list                                       │
└──────────────────────────────────────────────────────────────┘
```

## SUSPEND USER Use Case

```
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
│ User clicks "Suspend" button on a user row                  │
│ User ID: 2                                                   │
└─────────────────────────────┬────────────────────────────────┘
                              │
         axios.put('/api/userAccount/2/suspend', {})
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ BOUNDARY: suspend_user_account_controller.py               │
│                                                              │
│ @route.route('/<int:user_id>/suspend', methods=['PUT'])   │
│ @require_role(Role.USER_ADMIN)                              │
│ def suspend(user_id):  ← user_id = 2                       │
│     User.update_user(user_id, {'is_active': False})       │
│     return 200 OK                                           │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ CONTROL: User.update_user(2, {'is_active': False})         │
│                                                              │
│ ✓ Rule 1: Verify user exists                               │
│   existing = User.get_user_by_id(2)                        │
│   if not existing: raise ValueError("User not found")      │
│                                                              │
│ ✓ Business logic: Update is_active to False               │
│                                                              │
│ ✓ All checks pass → Call Entity layer                      │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ ENTITY: Database Update                                     │
│                                                              │
│ supabase.table('users').update({'is_active': False})       │
│                          .eq('id', 2)                       │
│                          .execute()                         │
│                                                              │
│ SQL Generated:                                              │
│ UPDATE users SET is_active = false WHERE id = 2            │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ DATABASE UPDATE                                              │
│                                                              │
│ Before:                          After:                     │
│ ┌────────┐                       ┌────────┐                │
│ │id  2   │                       │id  2   │                │
│ │is_active: true  ──UPDATE─→  │is_active: false│             │
│ └────────┘                       └────────┘                │
│                                                              │
│ User with id=2 is now SUSPENDED                            │
│ (Cannot login anymore)                                      │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ BOUNDARY: Format Response                                   │
│                                                              │
│ return {                                                    │
│     'success': True,                                        │
│     'message': 'User suspended successfully',               │
│     'data': {...updated user...}                            │
│ }, 200                                                      │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
│ ✓ Shows "User suspended successfully"                       │
│ ✓ Updates user status to "Suspended"                        │
│ ✓ Changes button from "Suspend" to "Activate"              │
│ ✓ Grays out user row                                        │
└──────────────────────────────────────────────────────────────┘
```

## CASCADE DELETE Use Case

```
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
│ User clicks "Delete" on a Profile/Role                      │
│ Profile ID: 5                                                │
│ Role Name: "Support Manager"                                 │
│ Associated Users: 3                                          │
└─────────────────────────────┬────────────────────────────────┘
                              │
      axios.delete('/api/userProfile/5/delete')
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ BOUNDARY: suspend_user_profile_controller.py               │
│                                                              │
│ @route.route('/<int:profile_id>/delete', methods=['DELETE'])
│ @require_role(Role.USER_ADMIN)                              │
│ def delete(profile_id):  ← profile_id = 5                  │
│                                                              │
│     profile = Role.get_role_by_id(5)                        │
│     if not profile: return 404                              │
│                                                              │
│     supabase.table('roles').delete().eq('id', 5).execute()  │
│     return 200 OK                                           │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ ENTITY: Database Delete                                     │
│                                                              │
│ supabase.table('roles').delete().eq('id', 5).execute()     │
│                                                              │
│ SQL Generated:                                              │
│ DELETE FROM roles WHERE id = 5                              │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ DATABASE CASCADE CONSTRAINT TRIGGERS!                        │
│                                                              │
│ Foreign Key Constraint Definition (at table creation):      │
│ ALTER TABLE users                                            │
│ ADD CONSTRAINT fk_users_roles                               │
│ FOREIGN KEY (role_id) REFERENCES roles(id)                 │
│ ON DELETE CASCADE  ← THIS TRIGGERS AUTOMATIC DELETION      │
│                                                              │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ DATABASE AUTOMATIC CASCADE DELETE EXECUTES                  │
│                                                              │
│ Step 1: Delete the role                                     │
│ DELETE FROM roles WHERE id = 5  ✓ DONE                     │
│                                                              │
│ Step 2: CASCADE constraint automatically deletes users     │
│ DELETE FROM users WHERE role_id = 5  ✓ AUTOMATIC           │
│                                                              │
│ Before:                          After:                     │
│ Roles:                           Roles:                     │
│ ┌─────┐                          ┌─────┐                    │
│ │id: 5│ ──DELETE──→              (empty)                    │
│ └─────┘                          ┌─────┐                    │
│                                                              │
│ Users:                           Users:                     │
│ ┌───────────────┐                ┌───────────────┐          │
│ │id: 10, role_id: 5│ DELETED │ │(removed)      │          │
│ │id: 11, role_id: 5│ ─ AUTO ─→ │(removed)      │          │
│ │id: 12, role_id: 5│ CASCADE │ │(removed)      │          │
│ └───────────────┘                ┌───────────────┐          │
│                                                              │
│ RESULT: All 3 users automatically deleted!                 │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ BOUNDARY: Format Response                                   │
│                                                              │
│ return {                                                    │
│     'success': True,                                        │
│     'message': 'Profile and 3 associated users deleted',   │
│ }, 200                                                      │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                             │
│ ✓ Shows confirmation: "Profile deleted with CASCADE"        │
│ ✓ Removes profile from list                                 │
│ ✓ Removes 3 users from user table                          │
│ ✓ Shows warning about cascaded deletions                   │
└──────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌──────────────────────────────────────────┐
│ CLIENT REQUEST (possibly invalid)         │
└────────────────┬─────────────────────────┘
                 │
                 ↓
        ┌──────────────────┐
        │ VALIDATION ERROR │
        └────────┬─────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ↓                         ↓
INPUT INVALID            MISSING FIELD
(bad type)              (required field)
│                         │
│                         │
│ Example:               Example:
│ age: "not a number"   email: (missing)
│                         │
└────────────┬───────────┴┘
             │
             ↓
    ┌──────────────────────────┐
    │ BOUNDARY LAYER           │
    │ Catches validation error │
    │                          │
    │ return jsonify({         │
    │   'success': false,      │
    │   'message': 'Invalid    │
    │             input'       │
    │ }), 400 Bad Request      │
    │                          │
    └──────────────┬───────────┘
                   │
                   ↓
        ┌──────────────────┐
        │ CLIENT RECEIVES  │
        │ 400 Bad Request  │
        │ with error msg   │
        └──────────────────┘

─────────────────────────────────────────────

┌──────────────────────────────────────────┐
│ CLIENT REQUEST (valid format, but...)    │
└────────────────┬─────────────────────────┘
                 │
                 ↓
        BOUNDARY LAYER ✓ PASSES
                 │
                 ↓
        ┌──────────────────────┐
        │ BUSINESS RULE ERROR  │
        │ (Control Layer)       │
        └────────────┬──────────┘
                     │
    ┌────────────────┴────────────────┐
    │                                 │
    ↓                                 ↓
UNIQUE VIOLATION          FOREIGN KEY ERROR
(email exists)            (role not found)
│                         │
│ Example:               Example:
│ Trying to create       Assigning role_id: 999
│ user with email        that doesn't exist
│ already in DB          │
│                         │
└────────────┬───────────┴┘
             │
             ↓
    ┌──────────────────────────┐
    │ CONTROL LAYER            │
    │ Raises exception:        │
    │ ValueError("Email        │
    │             exists")     │
    │                          │
    │ Exception propagates UP  │
    └──────────────┬───────────┘
                   │
                   ↓
    ┌──────────────────────────┐
    │ BOUNDARY CATCHES         │
    │ exception in try/except  │
    │                          │
    │ return jsonify({         │
    │   'success': false,      │
    │   'message': str(error)  │
    │ }), 400 Bad Request      │
    │                          │
    └──────────────┬───────────┘
                   │
                   ↓
        ┌──────────────────────┐
        │ CLIENT RECEIVES      │
        │ 400 Bad Request      │
        │ "Email already       │
        │  exists"             │
        └──────────────────────┘

─────────────────────────────────────────────

┌──────────────────────────────────────────┐
│ DATABASE CONNECTION FAILS                │
└────────────────┬─────────────────────────┘
                 │
                 ↓
    ┌──────────────────────────┐
    │ ENTITY LAYER             │
    │ Database operation fails │
    │ Exception raised         │
    └──────────────┬───────────┘
                   │
                   ↓
    ┌──────────────────────────┐
    │ BOUNDARY CATCHES ALL     │
    │ EXCEPTIONS               │
    │                          │
    │ except Exception as e:   │
    │   return jsonify({       │
    │     'success': false,    │
    │     'message':           │
    │       str(e)             │
    │   }), 500 Server Error   │
    │                          │
    └──────────────┬───────────┘
                   │
                   ↓
        ┌──────────────────────┐
        │ CLIENT RECEIVES      │
        │ 500 Internal Error   │
        │ (check server logs)  │
        └──────────────────────┘
```

---

## Controller File Organization

```
src/controller/
│
├── auth/                                    # Authentication
│   ├── __init__.py
│   ├── auth_middleware.py                  # JWT verification
│   ├── login_controller.py                 # BOUNDARY: POST /api/auth/login
│   └── logout_controller.py                # BOUNDARY: POST /api/auth/logout
│
├── userAccount/                           # User CRUD Operations
│   ├── __init__.py
│   ├── create_user_account_controller.py  # BOUNDARY: POST /api/userAccount
│   ├── view_user_account_controller.py    # BOUNDARY: GET /api/userAccount
│   ├── update_user_account_controller.py  # BOUNDARY: PUT /api/userAccount/<id>
│   ├── suspend_user_account_controller.py # BOUNDARY: PUT suspend/activate/DELETE
│   └── search_user_account_controller.py  # BOUNDARY: POST /api/userAccount/search
│
└── userProfile/                           # Profile/Role CRUD Operations
    ├── __init__.py
    ├── create_user_profile_controller.py  # BOUNDARY: POST /api/userProfile
    ├── view_user_profile_controller.py    # BOUNDARY: GET /api/userProfile
    ├── update_user_profile_controller.py  # BOUNDARY: PUT /api/userProfile/<id>
    ├── suspend_user_profile_controller.py # BOUNDARY: DELETE /api/userProfile/<id>/delete
    └── search_user_profile_controller.py  # BOUNDARY: POST /api/userProfile/search

src/entity/
│
├── __init__.py
├── supabase_config.py                    # ENTITY: Database configuration
├── user.py                               # CONTROL + ENTITY: User business logic
├── role.py                               # CONTROL + ENTITY: Role business logic
├── profile.py                            # CONTROL + ENTITY: Profile business logic
├── request.py                            # CONTROL + ENTITY: Request business logic
└── csr_request.py                        # CONTROL + ENTITY: CSR Request business logic
```
