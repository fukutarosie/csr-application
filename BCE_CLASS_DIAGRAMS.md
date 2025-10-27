# BCE Class Diagrams - CSR Application

## Overview

This document provides comprehensive class diagrams for the CSR Application following the Boundary-Control-Entity (BCE) architecture pattern. Each diagram shows the structure and relationships between classes across all three layers.

---

## 1. LOGIN FEATURE - CLASS DIAGRAM

### Complete Class Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BOUNDARY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ LoginPage (Frontend Component)                                   │   │
│  │ src/app/page.js                                                  │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - formData: {username, password, role_name}                     │   │
│  │  - error: string                                                 │   │
│  │  - loading: boolean                                              │   │
│  │  - router: NextRouter                                            │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + handleChange(e): void                                         │   │
│  │  + handleSubmit(e): Promise<void>                                │   │
│  │  + render(): JSX.Element                                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Calls HTTP POST                                             │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ LoginController (Backend Boundary - Consolidated)                │   │
│  │ src/controller/auth/login_controller.py                          │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Handles all 3 authentication endpoints:                          │   │
│  │  ✓ POST /api/auth/login                                          │   │
│  │  ✓ POST /api/auth/logout                                         │   │
│  │  ✓ GET /api/auth/verify                                          │   │
│  │                                                                  │   │
│  │ Attributes:                                                      │   │
│  │  - login_blueprint: Blueprint                                    │   │
│  │  - request: Request                                              │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + login(request): Response                                      │   │
│  │  + logout(request): Response                                     │   │
│  │  + verify_session(request): Response                             │   │
│  │  - extract_and_sanitize_auth_data(data): dict                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │ Uses
         ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       CONTROL LAYER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ User (Control/Entity)                                            │   │
│  │ src/entity/user.py                                               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - user_id: uuid                                                 │   │
│  │  - username: string                                              │   │
│  │  - password_hash: string                                          │   │
│  │  - email: string                                                 │   │
│  │  - full_name: string                                             │   │
│  │  - role_id: uuid                                                 │   │
│  │  - is_active: boolean                                            │   │
│  │  - created_at: datetime                                          │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + verify_password(password): bool                               │   │
│  │  + hash_password(password): string                                │   │
│  │  + get_by_username(username): User                               │   │
│  │  + authenticate(username, password): User | None                 │   │
│  │  + get_user_details(user_id): dict                               │   │
│  │  + create_user(data): User                                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Uses                                                         │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Role (Control/Entity)                                            │   │
│  │ src/entity/role.py                                               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - role_id: uuid                                                 │   │
│  │  - role_name: string                                             │   │
│  │  - dashboard_route: string                                       │   │
│  │  - permissions: list                                             │   │
│  │  - created_at: datetime                                          │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + get_by_name(role_name): Role                                  │   │
│  │  + get_role_details(role_id): dict                               │   │
│  │  + get_permissions(role_id): list                                │   │
│  │  + verify_role_active(role_id): bool                             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │ Persists to
         ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        ENTITY LAYER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Supabase (Database Persistence)                                  │   │
│  │ src/entity/supabase_config.py                                    │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - SUPABASE_URL: string                                          │   │
│  │  - SUPABASE_KEY: string                                          │   │
│  │  - supabase_client: Client                                       │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + get_supabase(): Client                                        │   │
│  │  + query_table(table_name, filters): list                        │   │
│  │  + insert_row(table_name, data): dict                            │   │
│  │  + update_row(table_name, data): dict                            │   │
│  │  + delete_row(table_name, id): bool                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Communicates with                                           │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ PostgreSQL Database (Supabase)                                   │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Tables:                                                          │   │
│  │  - users (user_id, username, password_hash, email, role_id...) │   │
│  │  - roles (role_id, role_name, dashboard_route, is_active)       │   │
│  │  - user_profiles (profile_id, user_id, role_id, ...)           │   │
│  │                                                                  │   │
│  │ Relationships:                                                   │   │
│  │  - users.role_id → roles.role_id (FK)                           │   │
│  │  - users.user_id ← user_profiles.user_id (CASCADE DELETE)       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Login Feature - Class Relationships

```
    Frontend Component              Backend Handler              Business Logic          Database
    ┌─────────────────┐            ┌──────────────┐           ┌──────────────┐        ┌──────────┐
    │  LoginPage      │            │    Login     │           │    User      │        │PostgreSQL│
    │ (React)         │            │ Controller   │           │  (Control)   │        │          │
    └────────┬────────┘            └──────┬───────┘           └──────┬───────┘        └────┬─────┘
             │                            │                         │                      │
             │ HTTP POST                  │ Receives                │ Calls               │
             ├───────────────────────────>│                         │ Methods             │
             │ /api/auth/login            │ validate_input()        │                     │
             │                            ├────────────────────────>│                     │
             │                            │                         │ SQL Query           │
             │                            │                         ├────────────────────>│
             │                            │                         │ SELECT * FROM users │
             │                            │                         │ WHERE username=?    │
             │                            │                         │                     │
             │ HTTP 200 + JWT             │                         │                     │
             │<─────────────────────────┬─┤                         │<────────────────────┤
             │ {success, data, message}│ │ generate_token()         │ user_data           │
             │                        │ │<────────────────────────┤                     │
             │                        │ │                         │                     │
             │ Save Token             │ │                         │                     │
             │ localStorage.token     │ │                         │                     │
             │ Redirect to Dashboard  │ │                         │                     │
             │                        │ │                         │                     │
             │ HTTP 401               │ │                         │                     │
             │<────────────────────────┤ │                         │                     │
             │ {success: false,        │ │                         │                     │
             │  message: error}        │ │                         │                     │
             │                        │ │                         │                     │
             │ Show Error Message     │ │                         │                     │
             │                        │ │                         │                     │
```

---

## 2. USER ADMIN FEATURE - CLASS DIAGRAM

### Complete Class Structure for User Management

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BOUNDARY LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ AdminDashboard (Frontend Component)                              │   │
│  │ src/app/admin/page.js                                            │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - users: User[]                                                 │   │
│  │  - profiles: Profile[]                                           │   │
│  │  - selectedUser: User | null                                     │   │
│  │  - isModalOpen: boolean                                          │   │
│  │  - loading: boolean                                              │   │
│  │  - filters: {username, email, role}                              │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + fetchAllUsers(): Promise<void>                                │   │
│  │  + handleCreateUser(data): Promise<void>                         │   │
│  │  + handleUpdateUser(id, data): Promise<void>                     │   │
│  │  + handleSuspendUser(id): Promise<void>                          │   │
│  │  + handleActivateUser(id): Promise<void>                         │   │
│  │  + handleDeleteUser(id): Promise<void>                           │   │
│  │  + handleSearchUsers(query): Promise<void>                       │   │
│  │  + render(): JSX.Element                                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           ├─ HTTP GET → /api/userAccount                               │
│           ├─ HTTP POST → /api/userAccount                              │
│           ├─ HTTP PUT → /api/userAccount/<id>                          │
│           ├─ HTTP PUT → /api/userAccount/<id>/suspend                  │
│           ├─ HTTP PUT → /api/userAccount/<id>/activate                 │
│           ├─ HTTP DELETE → /api/userAccount/<id>/delete                │
│           └─ HTTP POST → /api/userAccount/search                       │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ UserAccountController (Backend Boundary Layer)                   │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Controllers Included:                                            │   │
│  │                                                                  │   │
│  │  ┌─ CreateUserAccountController                                 │   │
│  │  │  Methods: handle_create(request): Response                   │   │
│  │  │                                                              │   │
│  │  ├─ ViewUserAccountController                                  │   │
│  │  │  Methods: handle_view(user_id): Response                    │   │
│  │  │           handle_view_all(): Response                       │   │
│  │  │                                                              │   │
│  │  ├─ UpdateUserAccountController                                │   │
│  │  │  Methods: handle_update(user_id, data): Response            │   │
│  │  │                                                              │   │
│  │  ├─ SuspendUserAccountController                               │   │
│  │  │  Methods: handle_suspend(user_id): Response                 │   │
│  │  │           handle_activate(user_id): Response                │   │
│  │  │                                                              │   │
│  │  └─ SearchUserAccountController                                │   │
│  │     Methods: handle_search(filters): Response                  │   │
│  │                                                                  │   │
│  │ Base Methods (In All Controllers):                              │   │
│  │  + validate_input(data): bool                                   │   │
│  │  + validate_permissions(user_role): bool                        │   │
│  │  + format_response(status, data, message): dict                 │   │
│  │  + handle_error(error): Response                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Delegates to Control Layer                                  │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ AuthMiddleware                                                   │   │
│  │ src/controller/auth/auth_middleware.py                           │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Methods:                                                         │   │
│  │  + verify_token(token): dict | None                             │   │
│  │  + check_role_permission(role, required_role): bool             │   │
│  │  + protect_route(required_role): decorator                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │ Uses
         ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       CONTROL LAYER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ User (Control/Entity)                                            │   │
│  │ src/entity/user.py                                               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - user_id: uuid                                                 │   │
│  │  - username: string                                              │   │
│  │  - password_hash: string                                          │   │
│  │  - email: string                                                 │   │
│  │  - full_name: string                                             │   │
│  │  - role_id: uuid                                                 │   │
│  │  - is_active: boolean                                            │   │
│  │  - created_at: datetime                                          │   │
│  │  - updated_at: datetime                                          │   │
│  │                                                                  │   │
│  │ Methods (CRUD):                                                 │   │
│  │  + create_user(username, email, password, role_id): User         │   │
│  │  + get_user(user_id): User                                       │   │
│  │  + get_all_users(): User[]                                       │   │
│  │  + update_user(user_id, data): User                              │   │
│  │  + delete_user(user_id): bool                                    │   │
│  │  + suspend_user(user_id): bool                                   │   │
│  │  + activate_user(user_id): bool                                  │   │
│  │  + search_users(filters): User[]                                 │   │
│  │                                                                  │   │
│  │ Methods (Utilities):                                             │   │
│  │  + verify_password(password): bool                               │   │
│  │  + hash_password(password): string                                │   │
│  │  + authenticate(username, password): User | None                 │   │
│  │  + get_user_details(user_id): dict                               │   │
│  │  + validate_user_data(data): bool                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ References                                                  │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Role (Control/Entity)                                            │   │
│  │ src/entity/role.py                                               │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - role_id: uuid                                                 │   │
│  │  - role_name: string                                             │   │
│  │  - dashboard_route: string                                       │   │
│  │  - permissions: list                                             │   │
│  │  - created_at: datetime                                          │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + get_by_name(role_name): Role                                  │   │
│  │  + get_role_details(role_id): dict                               │   │
│  │  + get_permissions(role_id): list                                │   │
│  │  + verify_role_active(role_id): bool                             │   │
│  │  + get_all_roles(): Role[]                                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ UserProfile (Control/Entity)                                     │   │
│  │ src/entity/profile.py                                            │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Attributes:                                                      │   │
│  │  - profile_id: uuid                                              │   │
│  │  - user_id: uuid                                                 │   │
│  │  - role_id: uuid                                                 │   │
│  │  - profile_data: json                                            │   │
│  │  - is_active: boolean                                            │   │
│  │  - created_at: datetime                                          │   │
│  │                                                                  │   │
│  │ Methods:                                                         │   │
│  │  + create_profile(user_id, role_id, data): Profile               │   │
│  │  + get_profile(profile_id): Profile                              │   │
│  │  + update_profile(profile_id, data): Profile                     │   │
│  │  + delete_profile(profile_id): bool                              │   │
│  │  + get_user_profiles(user_id): Profile[]                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │ Persists to
         ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        ENTITY LAYER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Supabase (Database Client)                                       │   │
│  │ src/entity/supabase_config.py                                    │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │ Database Operations:                                             │   │
│  │  + table('users').select('*')                                    │   │
│  │  + table('users').insert(data)                                   │   │
│  │  + table('users').update(data).eq('user_id', id)                 │   │
│  │  + table('users').delete().eq('user_id', id)                     │   │
│  │                                                                  │   │
│  │ Related Tables:                                                  │   │
│  │  + table('roles').select('*')                                    │   │
│  │  + table('user_profiles').select('*')                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│           │                                                              │
│           │ Communicates with                                           │
│           ↓                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ PostgreSQL Database Tables (Supabase)                            │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │ ┌─────────────────────────┐                                     │   │
│  │ │ users                   │                                     │   │
│  │ ├─────────────────────────┤                                     │   │
│  │ │ user_id (PK)            │                                     │   │
│  │ │ username (UNIQUE)       │                                     │   │
│  │ │ password_hash           │                                     │   │
│  │ │ email                   │                                     │   │
│  │ │ full_name               │                                     │   │
│  │ │ role_id (FK → roles)    │───┐                               │   │
│  │ │ is_active               │   │                               │   │
│  │ │ created_at              │   │                               │   │
│  │ │ updated_at              │   │                               │   │
│  │ └─────────────────────────┘   │                               │   │
│  │           △                   │                               │   │
│  │           │ Has One           │                               │   │
│  │           └────────────────┬─ │                               │   │
│  │                           │ │                               │   │
│  │ ┌─────────────────────────┤─┴──────────────────────────────┐  │   │
│  │ │ user_profiles           │                                │  │   │
│  │ ├─────────────────────────┴────────────────────────────────┤  │   │
│  │ │ profile_id (PK)                                          │  │   │
│  │ │ user_id (FK → users) CASCADE DELETE                      │  │   │
│  │ │ role_id (FK → roles)                                    │  │   │
│  │ │ profile_data (JSON)                                     │  │   │
│  │ │ is_active                                               │  │   │
│  │ │ created_at                                              │  │   │
│  │ └────────────────────────────────────────────────────────┘  │   │
│  │                                                                  │   │
│  │ ┌────────────────────────────────────────────────────────────┐  │   │
│  │ │ roles                                                      │  │   │
│  │ ├────────────────────────────────────────────────────────────┤  │   │
│  │ │ role_id (PK)                                              │  │   │
│  │ │ role_name (UNIQUE)                                        │  │   │
│  │ │ dashboard_route                                           │  │   │
│  │ │ permissions (JSON)                                        │  │   │
│  │ │ is_active                                                 │  │   │
│  │ │ created_at                                                │  │   │
│  │ └────────────────────────────────────────────────────────────┘  │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### User Admin Feature - Class Relationships

```
     Frontend Admin           Backend Controllers          Control Services       Database Layer
     ┌──────────────┐         ┌──────────────────┐        ┌──────────────┐      ┌──────────────┐
     │   Admin UI   │         │  UserAccount     │        │    User      │      │  PostgreSQL  │
     │ admin/page.js│         │  Controllers     │        │   (Control)  │      │              │
     └──────┬───────┘         └────────┬─────────┘        └──────┬───────┘      └──────┬───────┘
            │                         │                         │                     │
            │ GET /api/userAccount   │                         │                     │
            ├────────────────────────>│ validate_input()        │                     │
            │                         ├────────────────────────>│ get_all_users()     │
            │                         │                         ├────────────────────>│
            │ [User List]             │                         │                     │ SELECT *
            │<────────────────────────┤<────────────────────────┤<────────────────────┤
            │                         │                         │                     │
            │ POST /api/userAccount   │                         │                     │
            ├────────────────────────>│ validate_input()        │                     │
            │ {username, pwd, role}   │ check permissions       │                     │
            │                         ├────────────────────────>│ create_user()       │
            │                         │                         ├────────────────────>│
            │ Success Response        │                         │                     │ INSERT
            │<────────────────────────┤<────────────────────────┤<────────────────────┤
            │                         │                         │                     │
            │ PUT /api/userAccount/:id│                         │                     │
            ├────────────────────────>│ validate_input()        │                     │
            │ {email, full_name, role}│                         │                     │
            │                         ├────────────────────────>│ update_user()       │
            │                         │                         ├────────────────────>│
            │ Updated User            │                         │                     │ UPDATE
            │<────────────────────────┤<────────────────────────┤<────────────────────┤
            │                         │                         │                     │
            │ PUT /api/userAccount/:id│                         │                     │
            ├───────────────/suspend─>│                         │                     │
            │                         ├────────────────────────>│ suspend_user()      │
            │                         │                         ├────────────────────>│
            │ Status: Suspended       │                         │                     │ UPDATE
            │<────────────────────────┤<────────────────────────┤<────────────────────┤
            │                         │                         │                     │
            │ DELETE /api/userAccount/:id                       │                     │
            ├────────────────────────>│ check permissions       │                     │
            │                         ├────────────────────────>│ delete_user()       │
            │                         │                         ├────────────────────>│
            │ Success/404             │                         │                     │ DELETE +
            │<────────────────────────┤<────────────────────────┤<────────────────────┤ CASCADE
            │                         │                         │                     │
            │ POST /api/userAccount/  │                         │                     │
            ├────search──────────────>│ validate_query()        │                     │
            │ {username: "john"}      │                         │                     │
            │                         ├────────────────────────>│ search_users()      │
            │                         │                         ├────────────────────>│
            │ [Filtered Results]      │                         │                     │ SELECT WHERE
            │<────────────────────────┤<────────────────────────┤<────────────────────┤
            │                         │                         │                     │
```

---

## 3. Class Inheritance Hierarchy

### Controller Classes

```
┌────────────────────────────────────┐
│     BaseController                 │
│  (Abstract Base Class)             │
├────────────────────────────────────┤
│ Methods:                           │
│  + validate_input()                │
│  + format_response()               │
│  + handle_error()                  │
│  + check_permissions()             │
└────────┬───────────────────────────┘
         │
         │ Extends
         ├──────────────────┬──────────────────┬──────────────────┐
         │                  │                  │                  │
         ↓                  ↓                  ↓                  ↓
    ┌─────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────────┐
    │ Login   │    │ Create   │    │ Suspend      │    │ Search       │
    │Ctrl     │    │ User     │    │ User         │    │ User         │
    │         │    │ Ctrl     │    │ Ctrl         │    │ Ctrl         │
    └─────────┘    └──────────┘    └──────────────┘    └──────────────┘
```

### Entity Classes

```
┌────────────────────────────────────┐
│     BaseEntity                     │
│  (Abstract Base Class)             │
├────────────────────────────────────┤
│ Methods:                           │
│  + validate_data()                 │
│  + get_by_id()                     │
│  + to_dict()                       │
└────────┬───────────────────────────┘
         │
         │ Extends
         ├──────────────┬──────────────┬──────────────┐
         │              │              │              │
         ↓              ↓              ↓              ↓
    ┌────────┐    ┌──────────┐  ┌─────────┐   ┌──────────┐
    │ User   │    │ Role     │  │ Profile │   │ Request  │
    │        │    │          │  │         │   │          │
    └────────┘    └──────────┘  └─────────┘   └──────────┘
         △
         │ Has One
         └──── Role
```

---

## 4. Data Flow Summary

### CREATE USER Flow

```
Frontend                 Boundary          Control            Entity
   │                        │                 │                 │
   │ handleCreateUser()      │                 │                 │
   ├───────────────────────> POST /api/       │                 │
   │                         userAccount      │                 │
   │                         │                 │                 │
   │                         │ validate_input()│                 │
   │                         ├───────────────> │                 │
   │                         │                 │                 │
   │                         │ check_perms()   │                 │
   │                         ├───────────────> │                 │
   │                         │                 │                 │
   │                         │ create_user()   │                 │
   │                         ├───────────────> │                 │
   │                         │                 │                 │
   │                         │                 │ DB INSERT       │
   │                         │                 ├────────────────>│
   │                         │                 │                 │
   │                         │                 │<────────────────┤
   │                         │                 │ new User obj    │
   │                         │                 │                 │
   │                         │ Success Response│                 │
   │<────────────────────────┤<────────────────┤                 │
   │ {success: true,         │                 │                 │
   │  data: new_user}        │                 │                 │
   │                         │                 │                 │
   │ Update UI               │                 │                 │
   └─ (refresh user list)    │                 │                 │
```

---

## 5. Method Signatures

### LoginPage Component

```python
handleChange(e: Event) -> void
  - Updates formData on input change
  - Parameters: React SyntheticEvent

handleSubmit(e: Event) -> Promise<void>
  - Sends login POST request
  - Handles response and redirects
  - Catches errors and displays them
  - Parameters: React SyntheticEvent
```

### Login Controller

```python
login_handler(request: Request) -> Response
  - Entry point for login API
  - Returns: {success, data, message}

validate_input(data: dict) -> bool
  - Validates username, password, role_name
  - Returns: True if valid, else raises Exception

format_response(status: str, data: dict, message: str) -> dict
  - Formats response object
  - Returns: {success, data, message}
```

### User Entity (Control Layer)

```python
authenticate(username: str, password: str) -> User | None
  - Verifies username and password
  - Returns: User object or None

get_by_username(username: str) -> User | None
  - Retrieves user from database
  - Returns: User object or None

verify_password(password: str) -> bool
  - Compares plain password with hash
  - Returns: True if match

hash_password(password: str) -> str
  - Hashes password using Werkzeug
  - Returns: Hashed password string
```

### User Admin Controller

```python
handle_create(request: Request) -> Response
  - Creates new user
  - Returns: {success, data, message}

handle_view(user_id: str) -> Response
  - Gets single user
  - Returns: {success, data, message}

handle_update(user_id: str, data: dict) -> Response
  - Updates user details
  - Returns: {success, data, message}

handle_suspend(user_id: str) -> Response
  - Suspends user account
  - Returns: {success, data, message}

handle_search(filters: dict) -> Response
  - Searches users by criteria
  - Returns: {success, data, message}
```

---

## Summary

This class diagram documentation provides:

✅ **Complete BCE structure** for Login and User Admin features
✅ **Class relationships** with multiplicity
✅ **Method signatures** and attributes
✅ **Data persistence flow** through all layers
✅ **Database schema** with foreign keys
✅ **Error handling** at each layer
✅ **Role-based access control** integration

Use these diagrams to understand the architecture patterns and how each layer communicates!

