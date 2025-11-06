# 📊 Complete System Diagrams - CSR Application

## BCE Pattern Clarification

**In our CSR Application:**
- **BOUNDARY** = Controllers (e.g., `LoginController`, `UserAccountController`)
  - Handle HTTP requests/responses
  - Located in `src/controller/`

- **CONTROL** = Entity Classes (e.g., `User`, `Role`, `Request`, `Shortlist`)
  - Contain business logic
  - Located in `src/entity/`

- **ENTITY** = Database Tables (e.g., `users`, `roles`, `requests`, `shortlist`)
  - Data persistence in Supabase PostgreSQL
  - Physical data storage

---

## Table of Contents
1. [BCE Class Diagram](#bce-class-diagram)
2. [Authentication Sequence Diagrams](#authentication-sequence-diagrams)
3. [User Account Management Sequence Diagrams](#user-account-management-sequence-diagrams)
4. [User Profile Management Sequence Diagrams](#user-profile-management-sequence-diagrams)
5. [Request Management Sequence Diagrams](#request-management-sequence-diagrams)
6. [Shortlist Management Sequence Diagrams](#shortlist-management-sequence-diagrams)

---

## BCE Class Diagram

### Complete System BCE Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BOUNDARY LAYER (Controllers)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐   │
│  │ LoginController    │  │ UserAccount        │  │ UserProfile        │   │
│  │                    │  │ Controllers        │  │ Controllers        │   │
│  ├────────────────────┤  ├────────────────────┤  ├────────────────────┤   │
│  │ +login()           │  │ +create()          │  │ +create()          │   │
│  │ +logout()          │  │ +view_all()        │  │ +view_all()        │   │
│  │ +verify()          │  │ +view_by_id()      │  │ +view_by_id()      │   │
│  └────────────────────┘  │ +update()          │  │ +update()          │   │
│                          │ +suspend()         │  │ +delete()          │   │
│                          │ +activate()        │  │ +search()          │   │
│                          │ +delete()          │  └────────────────────┘   │
│                          │ +search()          │                            │
│                          └────────────────────┘                            │
│                                                                               │
│  ┌────────────────────┐  ┌────────────────────┐                            │
│  │ Request            │  │ Shortlist          │                            │
│  │ Controllers        │  │ Controllers        │                            │
│  ├────────────────────┤  ├────────────────────┤                            │
│  │ +create()          │  │ +add()             │                            │
│  │ +view()            │  │ +get()             │                            │
│  │ +update()          │  │ +remove()          │                            │
│  │ +suspend()         │  │ +update_status()   │                            │
│  │ +search()          │  └────────────────────┘                            │
│  │ +get_analytics()   │                                                     │
│  └────────────────────┘                                                     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP Request/Response
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTROL LAYER (Entity Classes)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ User (Entity)                                                   │        │
│  ├────────────────────────────────────────────────────────────────┤        │
│  │ - id: int                                                       │        │
│  │ - username: str                                                 │        │
│  │ - password_hash: str                                            │        │
│  │ - full_name: str                                                │        │
│  │ - email: str                                                    │        │
│  │ - role_id: int                                                  │        │
│  │ - is_active: bool                                               │        │
│  ├────────────────────────────────────────────────────────────────┤        │
│  │ +authenticate_user(username, password, role): dict              │        │
│  │ +create_user(data): dict                                        │        │
│  │ +get_user_by_id(user_id): dict                                 │        │
│  │ +get_all_users(): list                                          │        │
│  │ +update_user(user_id, data): bool                              │        │
│  │ +suspend_user(user_id): bool                                   │        │
│  │ +activate_user(user_id): bool                                  │        │
│  │ +delete_user(user_id): bool                                    │        │
│  │ +search_users(criteria): list                                  │        │
│  │ +generate_jwt_token(user): str                                 │        │
│  │ +verify_token(token): dict                                     │        │
│  │ +invalidate_session_token(token): bool                         │        │
│  │ +log_user_activity(user_id, action, details): bool            │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ Role (Entity)                                                   │        │
│  ├────────────────────────────────────────────────────────────────┤        │
│  │ - id: int                                                       │        │
│  │ - role_name: str                                                │        │
│  │ - role_code: str                                                │        │
│  │ - description: str                                              │        │
│  │ - dashboard_route: str                                          │        │
│  ├────────────────────────────────────────────────────────────────┤        │
│  │ +get_all_roles(): list                                          │        │
│  │ +get_role_by_id(role_id): dict                                 │        │
│  │ +get_role_by_code(role_code): dict                             │        │
│  │ +create_role(data): dict                                        │        │
│  │ +update_role(role_id, data): bool                              │        │
│  │ +delete_role(role_id): bool (CASCADE DELETE)                   │        │
│  │ +search_roles(search_term): list                               │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ Request (Entity)                                                │        │
│  ├────────────────────────────────────────────────────────────────┤        │
│  │ - id: int                                                       │        │
│  │ - pin_user_id: int                                              │        │
│  │ - title: str                                                    │        │
│  │ - description: str                                              │        │
│  │ - category: str                                                 │        │
│  │ - status: str                                                   │        │
│  │ - budget_min: decimal                                           │        │
│  │ - budget_max: decimal                                           │        │
│  │ - timeline: date                                                │        │
│  │ - created_at: timestamp                                         │        │
│  ├────────────────────────────────────────────────────────────────┤        │
│  │ +create_request(data): dict                                     │        │
│  │ +get_request_by_id(request_id): dict                           │        │
│  │ +get_requests_by_user(user_id): list                           │        │
│  │ +update_request(request_id, data): bool                        │        │
│  │ +suspend_request(request_id): bool                             │        │
│  │ +search_requests(criteria): list                               │        │
│  │ +get_request_analytics(): dict                                 │        │
│  │ +get_completed_matches(user_id): list                          │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ Shortlist (Entity)                                              │        │
│  ├────────────────────────────────────────────────────────────────┤        │
│  │ - id: int                                                       │        │
│  │ - csr_rep_id: int                                               │        │
│  │ - request_id: int                                               │        │
│  │ - status: str                                                   │        │
│  │ - notes: str                                                    │        │
│  │ - added_at: timestamp                                           │        │
│  ├────────────────────────────────────────────────────────────────┤        │
│  │ +add_to_shortlist(data): dict                                  │        │
│  │ +get_shortlist_by_user(user_id): list                          │        │
│  │ +get_shortlist_item(shortlist_id): dict                        │        │
│  │ +update_shortlist_status(shortlist_id, status): bool           │        │
│  │ +remove_from_shortlist(shortlist_id): bool                     │        │
│  │ +check_if_shortlisted(user_id, request_id): bool               │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ SQL Queries
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATABASE TABLES (Data Persistence)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │   users     │   │    roles    │   │  requests   │   │  shortlist  │   │
│  ├─────────────┤   ├─────────────┤   ├─────────────┤   ├─────────────┤   │
│  │ id (PK)     │   │ id (PK)     │   │ id (PK)     │   │ id (PK)     │   │
│  │ username    │   │ role_name   │   │ pin_user_id │   │ csr_rep_id  │   │
│  │ password    │   │ role_code   │   │ title       │   │ request_id  │   │
│  │ full_name   │   │ description │   │ description │   │ status      │   │
│  │ email       │   │ dashboard   │   │ category    │   │ notes       │   │
│  │ role_id(FK) │   │             │   │ status      │   │ added_at    │   │
│  │ is_active   │   │             │   │ budget_min  │   │             │   │
│  │ created_at  │   │             │   │ budget_max  │   │             │   │
│  └─────────────┘   └─────────────┘   │ timeline    │   └─────────────┘   │
│        │                  ▲           │ created_at  │           │          │
│        └──────────────────┘           └─────────────┘           │          │
│                                              ▲                   │          │
│                                              │                   │          │
│                                              └───────────────────┘          │
│                                                                               │
│  Supabase PostgreSQL Database                                               │
│  - Row Level Security (RLS)                                                 │
│  - CASCADE DELETE on role deletion                                          │
│  - Indexes on foreign keys                                                  │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Authentication Sequence Diagrams

### 1. User Login Flow

```
┌────────┐       ┌─────────────┐       ┌──────────┐       ┌──────────┐
│ Client │       │LoginCtrl    │       │ User     │       │ Role     │
│(Next.js│       │(Boundary)   │       │(Control) │       │(Control) │
└────┬───┘       └──────┬──────┘       └────┬─────┘       └────┬─────┘
     │                  │                    │                   │
     │ 1. POST /login   │                    │                   │
     │ {username,pwd,   │                    │                   │
     │  role_name}      │                    │                   │
     ├─────────────────>│                    │                   │
     │                  │                    │                   │
     │                  │ 2. Validate JSON   │                   │
     │                  │    & fields        │                   │
     │                  │───┐                │                   │
     │                  │   │                │                   │
     │                  │<──┘                │                   │
     │                  │                    │                   │
     │                  │ 3. Sanitize input  │                   │
     │                  │───┐                │                   │
     │                  │   │                │                   │
     │                  │<──┘                │                   │
     │                  │                    │                   │
     │                  │ 4. authenticate_   │                   │
     │                  │    user(username,  │                   │
     │                  │    password,role)  │                   │
     │                  ├───────────────────>│                   │
     │                  │                    │                   │
     │                  │                    │ 5. Query user     │
     │                  │                    │    by username    │
     │                  │                    ├──────────┐        │
     │                  │                    │          │        │
     │                  │                    │<─────────┘        │
     │                  │                    │                   │
     │                  │                    │ 6. Verify         │
     │                  │                    │    password       │
     │                  │                    ├──────────┐        │
     │                  │                    │          │        │
     │                  │                    │<─────────┘        │
     │                  │                    │                   │
     │                  │                    │ 7. get_role_by_id │
     │                  │                    │   (role_id)       │
     │                  │                    ├──────────────────>│
     │                  │                    │                   │
     │                  │                    │ 8. role details   │
     │                  │                    │<──────────────────┤
     │                  │                    │                   │
     │                  │                    │ 9. Generate JWT   │
     │                  │                    ├──────────┐        │
     │                  │                    │          │        │
     │                  │                    │<─────────┘        │
     │                  │                    │                   │
     │                  │ 10. {token, user   │                   │
     │                  │     data, role}    │                   │
     │                  │<───────────────────┤                   │
     │                  │                    │                   │
     │                  │ 11. Log activity   │                   │
     │                  │<───────────────────┤                   │
     │                  │                    │                   │
     │                  │ 12. Format success │                   │
     │                  │     response       │                   │
     │                  │───┐                │                   │
     │                  │   │                │                   │
     │                  │<──┘                │                   │
     │                  │                    │                   │
     │ 13. 200 OK       │                    │                   │
     │ {success: true,  │                    │                   │
     │  data: {token,   │                    │                   │
     │  user{...}}}     │                    │                   │
     │<─────────────────┤                    │                   │
     │                  │                    │                   │
```

### 2. Token Verification Flow

```
┌────────┐       ┌─────────────┐       ┌──────────┐       ┌──────────┐
│ Client │       │LoginCtrl    │       │ User     │       │ Role     │
└────┬───┘       └──────┬──────┘       └────┬─────┘       └────┬─────┘
     │                  │                    │                   │
     │ 1. GET /verify   │                    │                   │
     │ Header: Bearer   │                    │                   │
     │ {token}          │                    │                   │
     ├─────────────────>│                    │                   │
     │                  │                    │                   │
     │                  │ 2. Extract token   │                   │
     │                  │    from header     │                   │
     │                  │───┐                │                   │
     │                  │   │                │                   │
     │                  │<──┘                │                   │
     │                  │                    │                   │
     │                  │ 3. verify_token()  │                   │
     │                  ├───────────────────>│                   │
     │                  │                    │                   │
     │                  │                    │ 4. Decode JWT     │
     │                  │                    ├──────────┐        │
     │                  │                    │          │        │
     │                  │                    │<─────────┘        │
     │                  │                    │                   │
     │                  │                    │ 5. Get user by ID │
     │                  │                    ├──────────┐        │
     │                  │                    │          │        │
     │                  │                    │<─────────┘        │
     │                  │                    │                   │
     │                  │ 6. user data       │                   │
     │                  │<───────────────────┤                   │
     │                  │                    │                   │
     │                  │ 7. get_role_by_id  │                   │
     │                  ├───────────────────────────────────────>│
     │                  │                    │                   │
     │                  │ 8. role details    │                   │
     │                  │<───────────────────────────────────────┤
     │                  │                    │                   │
     │ 9. 200 OK        │                    │                   │
     │ {success: true,  │                    │                   │
     │  data: {user}}   │                    │                   │
     │<─────────────────┤                    │                   │
     │                  │                    │                   │
```

### 3. Logout Flow

```
┌────────┐       ┌─────────────┐       ┌──────────┐
│ Client │       │LoginCtrl    │       │ User     │
└────┬───┘       └──────┬──────┘       └────┬─────┘
     │                  │                    │
     │ 1. POST /logout  │                    │
     │ Header: Bearer   │                    │
     │ {token}          │                    │
     ├─────────────────>│                    │
     │                  │                    │
     │                  │ 2. Extract token   │
     │                  │───┐                │
     │                  │   │                │
     │                  │<──┘                │
     │                  │                    │
     │                  │ 3. invalidate_     │
     │                  │    session_token() │
     │                  ├───────────────────>│
     │                  │                    │
     │                  │                    │ 4. Add to        │
     │                  │                    │    revoked_tokens│
     │                  │                    ├──────────┐       │
     │                  │                    │          │       │
     │                  │                    │<─────────┘       │
     │                  │                    │                  │
     │                  │ 5. true            │                  │
     │                  │<───────────────────┤                  │
     │                  │                    │                  │
     │ 6. 200 OK        │                    │                  │
     │ {success: true,  │                    │                  │
     │  message:        │                    │                  │
     │  "Logged out"}   │                    │                  │
     │<─────────────────┤                    │                  │
     │                  │                    │                  │
```

---

## User Account Management Sequence Diagrams

### 4. Create User Account

```
┌────────┐       ┌─────────────────┐       ┌──────────┐       ┌──────────┐
│ Admin  │       │CreateUserAccCtrl│       │ User     │       │ Role     │
│ Client │       │(Boundary)       │       │(Control) │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘       └────┬─────┘
     │                    │                      │                   │
     │ 1. POST /userAcct  │                      │                   │
     │ {username, pwd,    │                      │                   │
     │  email, full_name, │                      │                   │
     │  role_id}          │                      │                   │
     ├───────────────────>│                      │                   │
     │                    │                      │                   │
     │                    │ 2. @require_role     │                   │
     │                    │    (USER_ADMIN)      │                   │
     │                    │───┐                  │                   │
     │                    │   │                  │                   │
     │                    │<──┘                  │                   │
     │                    │                      │                   │
     │                    │ 3. Validate fields   │                   │
     │                    │───┐                  │                   │
     │                    │   │                  │                   │
     │                    │<──┘                  │                   │
     │                    │                      │                   │
     │                    │ 4. Sanitize input    │                   │
     │                    │───┐                  │                   │
     │                    │   │                  │                   │
     │                    │<──┘                  │                   │
     │                    │                      │                   │
     │                    │ 5. Verify role_id    │                   │
     │                    │      exists          │                   │
     │                    ├─────────────────────────────────────────>│
     │                    │                      │                   │
     │                    │ 6. role exists       │                   │
     │                    │<─────────────────────────────────────────┤
     │                    │                      │                   │
     │                    │ 7. create_user(data) │                   │
     │                    ├─────────────────────>│                   │
     │                    │                      │                   │
     │                    │                      │ 8. Hash password  │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │                      │ 9. Insert to DB   │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 10. new user data    │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 11. 201 Created    │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: {user}}     │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 5. View All Users

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ Admin  │       │ViewUserAccCtrl  │       │ User     │
│ Client │       │(Boundary)       │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. GET /userAcct   │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. @require_role     │
     │                    │    (USER_ADMIN)      │
     │                    │───┐                  │
     │                    │   │                  │
     │                    │<──┘                  │
     │                    │                      │
     │                    │ 3. get_all_users()   │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 4. Query all users│
     │                    │                      │    with JOIN roles│
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 5. list of users     │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 6. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: [users...], │                      │                   │
     │  count: 36}        │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 6. Update User Account

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ Admin  │       │UpdateUserAccCtrl│       │ User     │
│ Client │       │(Boundary)       │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. PUT /userAcct/5 │                      │
     │ {full_name,email}  │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. Validate & check  │
     │                    │    user exists       │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │ 3. user exists       │
     │                    │<─────────────────────┤
     │                    │                      │
     │                    │ 4. update_user(5,    │
     │                    │    {data})           │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 5. Update DB      │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 6. true              │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 7. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  message: "User    │                      │                   │
     │  updated"}         │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 7. Suspend/Delete User Account

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ Admin  │       │SuspendUserAccCtrl│      │ User     │
│ Client │       │(Boundary)       │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. PUT /userAcct/5 │                      │
     │    /suspend        │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. suspend_user(5)   │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 3. Set is_active  │
     │                    │                      │    = false        │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 4. true              │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 5. 200 OK          │                      │                   │
     │ {success: true}    │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 8. Search Users

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ Admin  │       │SearchUserAccCtrl│       │ User     │
│ Client │       │(Boundary)       │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. POST /userAcct/ │                      │
     │    search          │                      │
     │ {username:"admin"} │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. search_users(     │
     │                    │    criteria)         │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 3. ILIKE query    │
     │                    │                      │    on username,   │
     │                    │                      │    email,fullname │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 4. filtered users    │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 5. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: [users...]} │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

---

## User Profile Management Sequence Diagrams

### 9. Create User Profile (Role)

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ Admin  │       │CreateUserProfile│       │ Role     │
│ Client │       │Ctrl (Boundary)  │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. POST /userProf  │                      │
     │ {role_name,        │                      │
     │  role_code,        │                      │
     │  description,      │                      │
     │  dashboard_route}  │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. Validate fields   │
     │                    │───┐                  │
     │                    │   │                  │
     │                    │<──┘                  │
     │                    │                      │
     │                    │ 3. create_role(data) │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 4. Check duplicate│
     │                    │                      │    role_code      │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │                      │ 5. Insert to DB   │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 6. new role data     │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 7. 201 Created     │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: {role}}     │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 10. Delete User Profile (CASCADE DELETE)

```
┌────────┐       ┌─────────────────┐       ┌──────────┐       ┌──────────┐
│ Admin  │       │SuspendUserProf  │       │ Role     │       │ User     │
│ Client │       │Ctrl (Boundary)  │       │(Control) │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘       └────┬─────┘
     │                    │                      │                   │
     │ 1. DELETE /userProf│                      │                   │
     │    /3/delete       │                      │                   │
     ├───────────────────>│                      │                   │
     │                    │                      │                   │
     │                    │ 2. Check role exists │                   │
     │                    ├─────────────────────>│                   │
     │                    │                      │                   │
     │                    │ 3. role data         │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │                    │ 4. Get users with    │                   │
     │                    │    this role         │                   │
     │                    ├─────────────────────────────────────────>│
     │                    │                      │                   │
     │                    │ 5. list of users     │                   │
     │                    │<─────────────────────────────────────────┤
     │                    │                      │                   │
     │                    │ 6. delete_role(3)    │                   │
     │                    │    [CASCADE]         │                   │
     │                    ├─────────────────────>│                   │
     │                    │                      │                   │
     │                    │                      │ 7. Delete role    │
     │                    │                      │    (triggers      │
     │                    │                      │    cascade delete │
     │                    │                      │    of users)      │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 8. true              │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 9. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  message: "Role    │                      │                   │
     │  deleted",         │                      │                   │
     │  affected_users: 5}│                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

---

## Request Management Sequence Diagrams

### 11. Create PIN Request

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ PIN    │       │CreatePINRequest │       │ Request  │
│ User   │       │Ctrl (Boundary)  │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. POST /requests  │                      │
     │ {title,description,│                      │
     │  category,budget,  │                      │
     │  timeline}         │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. @require_role(PIN)│
     │                    │───┐                  │
     │                    │   │                  │
     │                    │<──┘                  │
     │                    │                      │
     │                    │ 3. Validate fields   │
     │                    │───┐                  │
     │                    │   │                  │
     │                    │<──┘                  │
     │                    │                      │
     │                    │ 4. create_request(   │
     │                    │    user_id, data)    │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 5. Insert to DB   │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 6. new request data  │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 7. 201 Created     │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: {request}}  │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 12. View PIN Requests

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ PIN    │       │GetPINRequests   │       │ Request  │
│ User   │       │Ctrl (Boundary)  │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. GET /requests   │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. get_requests_by_  │
     │                    │    user(user_id)     │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 3. Query requests │
     │                    │                      │    WHERE pin_user │
     │                    │                      │    _id = user_id  │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 4. list of requests  │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 5. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: [requests]}│                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 13. Search Requests (CSR Rep)

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ CSR    │       │SearchPINRequest │       │ Request  │
│ Rep    │       │Ctrl (Boundary)  │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. POST /requests/ │                      │
     │    search          │                      │
     │ {category, status, │                      │
     │  budget_range}     │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. @require_role     │
     │                    │    (CSR_REP)         │
     │                    │───┐                  │
     │                    │   │                  │
     │                    │<──┘                  │
     │                    │                      │
     │                    │ 3. search_requests(  │
     │                    │    criteria)         │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 4. Query with     │
     │                    │                      │    filters        │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 5. filtered requests │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 6. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: [requests], │                      │                   │
     │  count: 15}        │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 14. Get Request Analytics

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ Admin/ │       │GetRequestAnalyt │       │ Request  │
│Platform│       │Ctrl (Boundary)  │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. GET /requests/  │                      │
     │    analytics       │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. get_request_      │
     │                    │    analytics()       │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 3. Aggregate      │
     │                    │                      │    queries:       │
     │                    │                      │    - COUNT by     │
     │                    │                      │      status       │
     │                    │                      │    - COUNT by     │
     │                    │                      │      category     │
     │                    │                      │    - AVG budget   │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 4. analytics data    │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 5. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: {           │                      │                   │
     │    total: 150,     │                      │                   │
     │    by_status: {...}│                      │                   │
     │    by_category:{..}│                      │                   │
     │  }}                │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

---

## Shortlist Management Sequence Diagrams

### 15. Add to Shortlist

```
┌────────┐       ┌─────────────────┐       ┌──────────┐       ┌──────────┐
│ CSR    │       │AddToShortlist   │       │Shortlist │       │ Request  │
│ Rep    │       │Ctrl (Boundary)  │       │(Control) │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘       └────┬─────┘
     │                    │                      │                   │
     │ 1. POST /shortlist │                      │                   │
     │ {request_id,notes} │                      │                   │
     ├───────────────────>│                      │                   │
     │                    │                      │                   │
     │                    │ 2. @require_role     │                   │
     │                    │    (CSR_REP)         │                   │
     │                    │───┐                  │                   │
     │                    │   │                  │                   │
     │                    │<──┘                  │                   │
     │                    │                      │                   │
     │                    │ 3. Verify request    │                   │
     │                    │    exists            │                   │
     │                    ├─────────────────────────────────────────>│
     │                    │                      │                   │
     │                    │ 4. request exists    │                   │
     │                    │<─────────────────────────────────────────┤
     │                    │                      │                   │
     │                    │ 5. Check if already  │                   │
     │                    │    shortlisted       │                   │
     │                    ├─────────────────────>│                   │
     │                    │                      │                   │
     │                    │ 6. not shortlisted   │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │                    │ 7. add_to_shortlist( │                   │
     │                    │    csr_id, req_id,   │                   │
     │                    │    notes)            │                   │
     │                    ├─────────────────────>│                   │
     │                    │                      │                   │
     │                    │                      │ 8. Insert to DB   │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 9. shortlist data    │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 10. 201 Created    │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: {shortlist}}│                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 16. Get My Shortlist

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ CSR    │       │GetShortlist     │       │Shortlist │
│ Rep    │       │Ctrl (Boundary)  │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. GET /shortlist  │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. get_shortlist_by_ │
     │                    │    user(csr_id)      │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 3. Query shortlist│
     │                    │                      │    with JOIN      │
     │                    │                      │    requests       │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 4. shortlist items   │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 5. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  data: [items...], │                      │                   │
     │  count: 8}         │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

### 17. Remove from Shortlist

```
┌────────┐       ┌─────────────────┐       ┌──────────┐
│ CSR    │       │RemoveFromShortl │       │Shortlist │
│ Rep    │       │Ctrl (Boundary)  │       │(Control) │
└────┬───┘       └────────┬────────┘       └────┬─────┘
     │                    │                      │
     │ 1. DELETE          │                      │
     │    /shortlist/25   │                      │
     ├───────────────────>│                      │
     │                    │                      │
     │                    │ 2. Verify ownership  │
     │                    │    (csr_rep_id ==    │
     │                    │    current_user_id)  │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │ 3. ownership OK      │
     │                    │<─────────────────────┤
     │                    │                      │
     │                    │ 4. remove_from_      │
     │                    │    shortlist(25)     │
     │                    ├─────────────────────>│
     │                    │                      │
     │                    │                      │ 5. DELETE from DB │
     │                    │                      ├──────────┐        │
     │                    │                      │          │        │
     │                    │                      │<─────────┘        │
     │                    │                      │                   │
     │                    │ 6. true              │                   │
     │                    │<─────────────────────┤                   │
     │                    │                      │                   │
     │ 7. 200 OK          │                      │                   │
     │ {success: true,    │                      │                   │
     │  message: "Removed │                      │                   │
     │  from shortlist"}  │                      │                   │
     │<───────────────────┤                      │                   │
     │                    │                      │                   │
```

---

## Summary

### Key Patterns Across All Diagrams:

1. **Three-Layer Architecture (BCE)**
   - **Boundary**: Controllers handle HTTP requests/responses
   - **Control**: Entity classes contain business logic
   - **Entity**: Database tables store data

2. **Authentication & Authorization**
   - JWT token-based authentication
   - Role-based access control using `@require_role` decorator
   - Token verification on protected endpoints

3. **Data Flow**
   - Client → Controller (Boundary) → Entity (Control) → Database (Entity)
   - Response flows back through the same layers

4. **Validation Layers**
   - HTTP format validation (Boundary layer)
   - Business logic validation (Control layer)
   - Database constraints (Entity layer)

5. **Error Handling**
   - Standardized error responses
   - Appropriate HTTP status codes (400, 401, 403, 404, 500)
   - Detailed error messages for debugging

6. **Security Features**
   - Password hashing (bcrypt)
   - Input sanitization
   - SQL injection protection
   - XSS protection
   - Role-based access control

---

## Files Referenced

### Controllers (Boundary Layer)
- `src/controller/auth/login_controller.py`
- `src/controller/userAccount/*.py`
- `src/controller/userProfile/*.py`
- `src/controller/request/*.py`
- `src/controller/shortlist/*.py`

### Entities (Control Layer)
- `src/entity/user.py`
- `src/entity/role.py`
- `src/entity/request.py`
- `src/entity/shortlist.py`

### Database Tables (Entity Layer)
- `users`
- `roles`
- `requests`
- `shortlist`

---

**Generated**: November 6, 2025  
**Project**: CSR Application - Corporate Social Responsibility Platform  
**Architecture**: BCE (Boundary-Control-Entity) Pattern
