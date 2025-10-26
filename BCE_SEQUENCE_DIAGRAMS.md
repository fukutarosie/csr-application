# BCE Sequence Diagrams - CSR Application

## Overview

This document provides comprehensive sequence diagrams showing the complete flow of interactions between Boundary, Control, and Entity layers for all major features.

---

## 1. LOGIN FEATURE - SEQUENCE DIAGRAM

### Successful Login Flow

```
User              LoginPage        LoginController    User           Supabase        Role
  │                  │                  │             │              │              │
  │ 1. Enter Creds   │                  │             │              │              │
  ├────────────────>│                  │             │              │              │
  │                  │                  │             │              │              │
  │ 2. Click Login   │                  │             │              │              │
  ├────────────────>│                  │             │              │              │
  │                  │                  │             │              │              │
  │                  │ 3. handleSubmit()│             │              │              │
  │                  │ fetch POST       │             │              │              │
  │                  ├─────────────────>│             │              │              │
  │                  │ /api/auth/login  │             │              │              │
  │                  │ {username,       │             │              │              │
  │                  │  password,       │             │              │              │
  │                  │  role_name}      │             │              │              │
  │                  │                  │             │              │              │
  │                  │                  │ 4. Validate │              │              │
  │                  │                  │ Input Data  │              │              │
  │                  │                  │ ✓ Valid    │              │              │
  │                  │                  │             │              │              │
  │                  │                  │ 5. Authenticate│            │              │
  │                  │                  ├────────────>│              │              │
  │                  │                  │             │ get_by_username()          │
  │                  │                  │             ├─────────────>│              │
  │                  │                  │             │              │ SELECT *     │
  │                  │                  │             │              │ FROM users   │
  │                  │                  │             │              │ WHERE username=?
  │                  │                  │             │              │              │
  │                  │                  │             │              │ ✓ User Found │
  │                  │                  │             │<─────────────┤              │
  │                  │                  │             │ user_data    │              │
  │                  │                  │             │              │              │
  │                  │                  │ 6. Verify   │              │              │
  │                  │                  │ Password    │              │              │
  │                  │                  ├────────────>│              │              │
  │                  │                  │             │ verify_password()         │
  │                  │                  │             │ ✓ Password OK│              │
  │                  │                  │             │              │              │
  │                  │                  │ 7. Get Role │              │              │
  │                  │                  │ Details     │              │              │
  │                  │                  │ ├──────────────────────────────────────>│
  │                  │                  │ │           │              │              │ SELECT *
  │                  │                  │ │           │              │              │ FROM roles
  │                  │                  │ │           │              │              │ WHERE role_name=?
  │                  │                  │ │           │              │              │
  │                  │                  │ │           │              │              │ ✓ Role Found
  │                  │                  │<──────────────────────────────────────┤
  │                  │                  │ role_data   │              │              │
  │                  │                  │             │              │              │
  │                  │                  │ 8. Generate │              │              │
  │                  │                  │ JWT Token   │              │              │
  │                  │                  │ Token Created              │              │
  │                  │                  │             │              │              │
  │                  │ 9. Return        │             │              │              │
  │                  │ Success + Token  │             │              │              │
  │                  │<─────────────────┤             │              │              │
  │                  │ {success: true,  │             │              │              │
  │                  │  data: {token,   │             │              │              │
  │                  │         user,    │             │              │              │
  │                  │         role}}   │             │              │              │
  │                  │                  │             │              │              │
  │ 10. Save Token   │                  │             │              │              │
  │ localStorage     │                  │             │              │              │
  │<────────────────┤                  │             │              │              │
  │                  │                  │             │              │              │
  │ 11. Redirect     │                  │             │              │              │
  │ to Dashboard     │                  │             │              │              │
  │                  │                  │             │              │              │
```

### Failed Login Flow - Invalid Credentials

```
User              LoginPage        LoginController    User           Supabase
  │                  │                  │             │              │
  │ 1. Enter Invalid │                  │             │              │
  │ Credentials      │                  │             │              │
  ├────────────────>│                  │             │              │
  │                  │                  │             │              │
  │ 2. Click Login   │                  │             │              │
  ├────────────────>│                  │             │              │
  │                  │                  │             │              │
  │                  │ 3. handleSubmit()│             │              │
  │                  ├─────────────────>│             │              │
  │                  │                  │             │              │
  │                  │                  │ 4. Validate │              │
  │                  │                  │ Input ✓     │              │
  │                  │                  │             │              │
  │                  │                  │ 5. Get User │              │
  │                  │                  ├────────────>│              │
  │                  │                  │             │ ✗ NOT FOUND  │
  │                  │                  │<────────────┤              │
  │                  │                  │             │              │
  │                  │ 6. Return Error  │             │              │
  │                  │ Response         │             │              │
  │                  │<─────────────────┤             │              │
  │                  │ {success: false, │             │              │
  │                  │  message:        │             │              │
  │                  │  "Invalid        │             │              │
  │                  │  username"}      │             │              │
  │                  │                  │             │              │
  │ 7. Display Error │                  │             │              │
  │ Message          │                  │             │              │
  │<────────────────┤                  │             │              │
  │                  │                  │             │              │
  │ 8. User Retries  │                  │             │              │
  │                  │                  │             │              │
```

### Login Error - Missing Fields

```
User              LoginPage        LoginController    User           Supabase
  │                  │                  │             │              │
  │ 1. Leave Fields  │                  │             │              │
  │ Empty            │                  │             │              │
  ├────────────────>│                  │             │              │
  │                  │                  │             │              │
  │ 2. Click Login   │                  │             │              │
  ├────────────────>│                  │             │              │
  │                  │                  │             │              │
  │                  │ 3. handleSubmit()│             │              │
  │                  ├─────────────────>│             │              │
  │                  │                  │             │              │
  │                  │                  │ 4. Validate │              │
  │                  │                  │ Input       │              │
  │                  │                  │ ✗ INVALID   │              │
  │                  │                  │ (missing    │              │
  │                  │                  │ required    │              │
  │                  │                  │ fields)     │              │
  │                  │                  │             │              │
  │                  │ 5. Return Error  │             │              │
  │                  │ Response         │             │              │
  │                  │<─────────────────┤             │              │
  │                  │ {success: false, │             │              │
  │                  │  message:        │             │              │
  │                  │  "Please fill    │             │              │
  │                  │  all required    │             │              │
  │                  │  fields"}        │             │              │
  │                  │                  │             │              │
  │ 6. Display Error │                  │             │              │
  │ Message          │                  │             │              │
  │<────────────────┤                  │             │              │
  │                  │                  │             │              │
```

---

## 2. USER ADMIN - CREATE USER SEQUENCE DIAGRAM

### Successful Create User Flow

```
Admin UI        CreateUserCtrl      User Entity         Role Entity        Supabase
  │                  │                  │                  │                │
  │ 1. Enter User    │                  │                  │                │
  │ Details          │                  │                  │                │
  ├────────────────>│                  │                  │                │
  │ {username,       │                  │                  │                │
  │  password,       │                  │                  │                │
  │  email,          │                  │                  │                │
  │  full_name,      │                  │                  │                │
  │  role_id}        │                  │                  │                │
  │                  │                  │                  │                │
  │ 2. Click Create  │                  │                  │                │
  ├────────────────>│                  │                  │                │
  │ POST             │                  │                  │                │
  │ /api/userAccount │                  │                  │                │
  │                  │                  │                  │                │
  │                  │ 3. Extract &     │                  │                │
  │                  │ Validate Input   │                  │                │
  │                  │ ✓ Valid          │                  │                │
  │                  │                  │                  │                │
  │                  │ 4. Verify Token  │                  │                │
  │                  │ (JWT Middleware) │                  │                │
  │                  │ ✓ Valid Token    │                  │                │
  │                  │ ✓ User Admin Role│                  │                │
  │                  │                  │                  │                │
  │                  │ 5. Verify Role   │                  │                │
  │                  │ Exists           │                  │                │
  │                  ├────────────────────────────────────>│                │
  │                  │ get_by_id(role_id)                  │                │
  │                  │                  │                  │ SELECT *       │
  │                  │                  │                  │ FROM roles     │
  │                  │                  │                  │ WHERE role_id=?│
  │                  │                  │                  │                │
  │                  │                  │                  │ ✓ Role Found   │
  │                  │<────────────────────────────────────┤                │
  │                  │ role_data        │                  │                │
  │                  │                  │                  │                │
  │                  │ 6. Create User   │                  │                │
  │                  ├────────────────>│                  │                │
  │                  │ create_user()    │                  │                │
  │                  │ {username,       │                  │                │
  │                  │  password_hash,  │                  │                │
  │                  │  email, ...}     │                  │                │
  │                  │                  │                  │                │
  │                  │                  │ 7. Hash          │                │
  │                  │                  │ Password         │                │
  │                  │                  │ ✓ Hashed         │                │
  │                  │                  │                  │                │
  │                  │                  │ 8. Validate      │                │
  │                  │                  │ User Data        │                │
  │                  │                  │ ✓ Valid          │                │
  │                  │                  │                  │                │
  │                  │                  │ 9. Insert User   │                │
  │                  │                  │ into DB          │                │
  │                  │                  ├──────────────────────────────────>│
  │                  │                  │ INSERT INTO users                 │
  │                  │                  │ (user_id, username, password_hash,│
  │                  │                  │  email, role_id, ...)            │
  │                  │                  │                  │                │
  │                  │                  │                  │                │
  │                  │                  │                  │ ✓ User Created │
  │                  │                  │<──────────────────────────────────┤
  │                  │                  │ new_user_id      │                │
  │                  │                  │                  │                │
  │                  │ 10. Return       │                  │                │
  │                  │ Success          │                  │                │
  │                  │<────────────────>│                  │                │
  │                  │ {success: true,  │                  │                │
  │                  │  data: {         │                  │                │
  │                  │    user_id,      │                  │                │
  │                  │    username,     │                  │                │
  │                  │    email, ...    │                  │                │
  │                  │  }}              │                  │                │
  │                  │                  │                  │                │
  │ 11. Display      │                  │                  │                │
  │ Success Message  │                  │                  │                │
  │ Refresh List     │                  │                  │                │
  │<────────────────┤                  │                  │                │
  │                  │                  │                  │                │
```

### Create User Error - Missing Permissions

```
Admin UI        UpdateUserCtrl      Middleware          Supabase
  │                  │                  │                  │
  │ 1. Click Create  │                  │                  │
  │ POST             │                  │                  │
  ├────────────────>│                  │                  │
  │ /api/userAccount │                  │                  │
  │ (CSR Rep Token)  │                  │                  │
  │                  │                  │                  │
  │                  │ 2. Verify Token  │                  │
  │                  ├─────────────────>│                  │
  │                  │                  │ Decode JWT       │
  │                  │                  │ ✓ Token Valid    │
  │                  │                  │ Role: CSR Rep    │
  │                  │                  │                  │
  │                  │ 3. Check Role    │                  │
  │                  │ Permission       │                  │
  │                  │<─────────────────┤                  │
  │                  │ ✗ DENIED         │                  │
  │                  │ (CSR Rep can't   │                  │
  │                  │ create users)    │                  │
  │                  │                  │                  │
  │ 4. Return 403    │                  │                  │
  │ Forbidden        │                  │                  │
  │<────────────────┤                  │                  │
  │ {success: false, │                  │                  │
  │  message:        │                  │                  │
  │  "Insufficient   │                  │                  │
  │  permissions"}   │                  │                  │
  │                  │                  │                  │
  │ 5. Display Error │                  │                  │
  │<────────────────┤                  │                  │
  │                  │                  │                  │
```

---

## 3. USER ADMIN - UPDATE USER SEQUENCE DIAGRAM

### Successful Update User Flow

```
Admin UI       UpdateUserCtrl      User Entity         Supabase
  │                  │                  │                │
  │ 1. Load User     │                  │                │
  │ Data             │                  │                │
  ├────────────────>│                  │                │
  │                  │                  │                │
  │                  │ 2. Fetch User    │                │
  │                  ├────────────────>│                │
  │                  │ get_user(user_id)                │
  │                  │                  │ SELECT *       │
  │                  │                  │ FROM users     │
  │                  │                  │ WHERE user_id=?│
  │                  │                  │                │
  │                  │                  │ ✓ User Found   │
  │                  │<────────────────┤                │
  │                  │ user_data        │                │
  │                  │                  │                │
  │ 3. Display User  │                  │                │
  │ Form with Data   │                  │                │
  │<────────────────┤                  │                │
  │                  │                  │                │
  │ 4. Edit Fields   │                  │                │
  │ (email,          │                  │                │
  │  full_name)      │                  │                │
  ├────────────────>│                  │                │
  │                  │                  │                │
  │ 5. Submit        │                  │                │
  │ PUT /api/        │                  │                │
  │ userAccount/:id  │                  │                │
  ├────────────────>│                  │                │
  │ {email, ...}     │                  │                │
  │                  │                  │                │
  │                  │ 6. Validate      │                │
  │                  │ Input ✓          │                │
  │                  │                  │                │
  │                  │ 7. Check Perms   │                │
  │                  │ ✓ Authorized     │                │
  │                  │                  │                │
  │                  │ 8. Update User   │                │
  │                  ├────────────────>│                │
  │                  │ update_user()    │                │
  │                  │                  │ UPDATE users   │
  │                  │                  │ SET email=?,   │
  │                  │                  │ full_name=?    │
  │                  │                  │ WHERE user_id=?│
  │                  │                  │                │
  │                  │                  │ ✓ Updated      │
  │                  │<────────────────┤                │
  │                  │ updated_user     │                │
  │                  │                  │                │
  │ 9. Return        │                  │                │
  │ Success          │                  │                │
  │<────────────────┤                  │                │
  │ {success: true,  │                  │                │
  │  data: {         │                  │                │
  │    user_id,      │                  │                │
  │    email,        │                  │                │
  │    ...           │                  │                │
  │  }}              │                  │                │
  │                  │                  │                │
  │ 10. Show Message │                  │                │
  │ & Update List    │                  │                │
  │<────────────────┤                  │                │
  │                  │                  │                │
```

---

## 4. USER ADMIN - SUSPEND USER SEQUENCE DIAGRAM

### Suspend User Flow

```
Admin UI       SuspendUserCtrl      User Entity         Supabase
  │                  │                  │                │
  │ 1. Select User   │                  │                │
  │ Click Suspend    │                  │                │
  ├────────────────>│                  │                │
  │ PUT /api/        │                  │                │
  │ userAccount/:id/ │                  │                │
  │ suspend          │                  │                │
  │                  │                  │                │
  │                  │ 2. Validate ID   │                │
  │                  │ ✓ Valid UUID     │                │
  │                  │                  │                │
  │                  │ 3. Verify Perms  │                │
  │                  │ (JWT) ✓ Admin    │                │
  │                  │                  │                │
  │                  │ 4. Get User      │                │
  │                  ├────────────────>│                │
  │                  │ get_user(id)     │ SELECT *       │
  │                  │                  │ FROM users     │
  │                  │                  │ WHERE user_id=?│
  │                  │                  │                │
  │                  │                  │ ✓ User Found   │
  │                  │<────────────────┤                │
  │                  │                  │                │
  │                  │ 5. Suspend User  │                │
  │                  ├────────────────>│                │
  │                  │ suspend_user(id) │ UPDATE users   │
  │                  │                  │ SET            │
  │                  │                  │ is_active=false│
  │                  │                  │ WHERE user_id=?│
  │                  │                  │                │
  │                  │                  │ ✓ Suspended    │
  │                  │<────────────────┤                │
  │                  │                  │                │
  │ 6. Return Status │                  │                │
  │<────────────────┤                  │                │
  │ {success: true,  │                  │                │
  │  data: {status:  │                  │                │
  │  'suspended'}}   │                  │                │
  │                  │                  │                │
  │ 7. Update UI     │                  │                │
  │ Mark as          │                  │                │
  │ Suspended        │                  │                │
  │<────────────────┤                  │                │
  │                  │                  │                │
```

---

## 5. USER ADMIN - DELETE USER WITH CASCADE SEQUENCE DIAGRAM

### Delete User Flow (Cascade Delete)

```
Admin UI       DeleteUserCtrl      User Entity         Supabase        User Profiles
  │                  │                  │                │                  │
  │ 1. Select User   │                  │                │                  │
  │ Click Delete     │                  │                │                  │
  ├────────────────>│                  │                │                  │
  │ DELETE /api/     │                  │                │                  │
  │ userAccount/:id/ │                  │                │                  │
  │ delete           │                  │                │                  │
  │                  │                  │                │                  │
  │                  │ 2. Confirm       │                │                  │
  │ (Show Dialog)    │ Request          │                │                  │
  │ "Are you sure?"  │                  │                │                  │
  ├────────────────>│                  │                │                  │
  │                  │                  │                │                  │
  │ 3. Click Yes     │                  │                │                  │
  ├────────────────>│                  │                │                  │
  │                  │                  │                │                  │
  │                  │ 4. Verify Token  │                │                  │
  │                  │ & Permissions    │                │                  │
  │                  │ ✓ Admin Role     │                │                  │
  │                  │                  │                │                  │
  │                  │ 5. Check Cascade │                │                  │
  │                  │ Delete Setup     │                │                  │
  │                  │ ✓ Cascade        │                │                  │
  │                  │ Configured       │                │                  │
  │                  │                  │                │                  │
  │                  │ 6. Delete User   │                │                  │
  │                  ├────────────────>│                │                  │
  │                  │ delete_user(id)  │ DELETE FROM    │                  │
  │                  │                  │ users WHERE    │                  │
  │                  │                  │ user_id = ?    │                  │
  │                  │                  │                │                  │
  │                  │                  │ CASCADE DELETE │                  │
  │                  │                  │ Applied        │                  │
  │                  │                  │                │ DELETE FROM      │
  │                  │                  │                │ user_profiles    │
  │                  │                  │                │ WHERE user_id=?  │
  │                  │                  │                │                  │
  │                  │                  │                │ ✓ Profiles       │
  │                  │                  │                │ Deleted Auto     │
  │                  │                  │                │                  │
  │                  │                  │ ✓ User +       │                  │
  │                  │                  │ All Profiles   │                  │
  │                  │                  │ Deleted        │                  │
  │                  │<────────────────────────────────────────────────────>│
  │                  │                  │                │                  │
  │ 7. Return        │                  │                │                  │
  │ Success          │                  │                │                  │
  │<────────────────┤                  │                │                  │
  │ {success: true,  │                  │                │                  │
  │  message:        │                  │                │                  │
  │  "User deleted   │                  │                │                  │
  │  with all        │                  │                │                  │
  │  profiles"}      │                  │                │                  │
  │                  │                  │                │                  │
  │ 8. Refresh List  │                  │                │                  │
  │<────────────────┤                  │                │                  │
  │                  │                  │                │                  │
```

---

## 6. USER ADMIN - SEARCH USERS SEQUENCE DIAGRAM

### Search Users Flow

```
Admin UI       SearchUserCtrl      User Entity         Supabase
  │                  │                  │                │
  │ 1. Enter Search  │                  │                │
  │ Criteria         │                  │                │
  │ (username,       │                  │                │
  │  email, role)    │                  │                │
  ├────────────────>│                  │                │
  │                  │                  │                │
  │ 2. Click Search  │                  │                │
  │ POST /api/       │                  │                │
  │ userAccount/     │                  │                │
  │ search           │                  │                │
  ├────────────────>│                  │                │
  │ {filters: {      │                  │                │
  │   username:      │                  │                │
  │   "john",        │                  │                │
  │   role: "CSR"    │                  │                │
  │ }}               │                  │                │
  │                  │                  │                │
  │                  │ 3. Validate      │                │
  │                  │ Filters ✓        │                │
  │                  │                  │                │
  │                  │ 4. Check Perms   │                │
  │                  │ ✓ Authorized     │                │
  │                  │                  │                │
  │                  │ 5. Build Query   │                │
  │                  ├────────────────>│                │
  │                  │ search_users()   │ SELECT *       │
  │                  │ filters:         │ FROM users     │
  │                  │ {username:'john' │ WHERE          │
  │                  │  role: 'CSR'}    │ username ILIKE │
  │                  │                  │ '%john%' AND   │
  │                  │                  │ role_id IN (   │
  │                  │                  │  SELECT role_id│
  │                  │                  │  FROM roles    │
  │                  │                  │  WHERE role_   │
  │                  │                  │  name='CSR')   │
  │                  │                  │                │
  │                  │                  │ ✓ 3 Results    │
  │                  │<────────────────┤                │
  │                  │ [users...]       │                │
  │                  │                  │                │
  │ 6. Return        │                  │                │
  │ Results          │                  │                │
  │<────────────────┤                  │                │
  │ {success: true,  │                  │                │
  │  data: [         │                  │                │
  │    {...user1},   │                  │                │
  │    {...user2},   │                  │                │
  │    {...user3}    │                  │                │
  │  ],              │                  │                │
  │  count: 3}       │                  │                │
  │                  │                  │                │
  │ 7. Display       │                  │                │
  │ Search Results   │                  │                │
  │<────────────────┤                  │                │
  │                  │                  │                │
```

---

## 7. COMPLETE INTERACTION FLOW - LOGIN → ADMIN DASHBOARD

### End-to-End Flow

```
User            LoginPage        LoginCtrl         AuthMiddleware      AdminPage       GetUsersCtrl    User Entity
  │                  │                  │                  │                │                │              │
  │ 1. Load App      │                  │                  │                │                │              │
  ├────────────────>│                  │                  │                │                │              │
  │                  │ 1a. Check Token  │                  │                │                │              │
  │                  │ in localStorage  │                  │                │                │              │
  │                  │ ✗ No Token       │                  │                │                │              │
  │                  │ Show Login Form  │                  │                │                │              │
  │                  │                  │                  │                │                │              │
  │ 2. Enter Creds   │                  │                  │                │                │              │
  ├────────────────>│                  │                  │                │                │              │
  │                  │                  │                  │                │                │              │
  │ 3. Submit Login  │                  │                  │                │                │              │
  ├────────────────>│                  │                  │                │                │              │
  │                  ├─────────────────>│                  │                │                │              │
  │                  │ POST /api/auth/  │                  │                │                │              │
  │                  │ login            │                  │                │                │              │
  │                  │                  │ 4. Validate &    │                │                │              │
  │                  │                  │ Authenticate     │                │                │              │
  │                  │                  │                  │                │                │              │
  │                  │                  │ 5. Generate JWT  │                │                │              │
  │                  │                  │ + User Data      │                │                │              │
  │                  │<─────────────────┤                  │                │                │              │
  │                  │ {success: true,  │                  │                │                │              │
  │                  │  data: {token,   │                  │                │                │              │
  │                  │         user}}   │                  │                │                │              │
  │                  │                  │                  │                │                │              │
  │ 6. Save Token    │                  │                  │                │                │              │
  │ Redirect /admin  │                  │                  │                │                │              │
  ├────────────────>│                  │                  │                │                │              │
  │                  │                  │                  │                │                │              │
  │                  │                  │                  │ 7. Load Admin  │                │              │
  │                  │                  │                  │ Page           │                │              │
  │                  │                  │                  ├───────────────>│                │              │
  │                  │                  │                  │                │                │              │
  │                  │                  │                  │ 8. Check Token │                │              │
  │                  │                  │                  │ in Header      │                │              │
  │                  │                  │                  │ ✓ Valid Token  │                │              │
  │                  │                  │                  │ Role: Admin    │                │              │
  │                  │                  │                  │                │                │              │
  │                  │                  │                  │ 9. Fetch Users │                │              │
  │                  │                  │                  │                ├──────────────>│              │
  │                  │                  │                  │                │ GET /api/     │              │
  │                  │                  │                  │                │ userAccount  │              │
  │                  │                  │                  │                │                │              │
  │                  │                  │                  │                │ 10. Validate │              │
  │                  │                  │                  │                │ & Get All    │              │
  │                  │                  │                  │                ├─────────────>│
  │                  │                  │                  │                │              │ get_all_users()
  │                  │                  │                  │                │              │ + SELECT *
  │                  │                  │                  │                │              │ FROM users
  │                  │                  │                  │                │              │
  │                  │                  │                  │                │              │ ✓ 10 Users
  │                  │                  │                  │                │<─────────────┤
  │                  │                  │                  │                │              │
  │                  │                  │                  │                │ 11. Return   │
  │                  │                  │                  │                │ User List    │
  │                  │                  │                  │                │<──────────────
  │                  │                  │                  │                │ [users...]   │
  │                  │                  │                  │                │              │
  │ 12. Display      │                  │                  │                │              │
  │ Admin Dashboard  │                  │                  │                │              │
  │ with User List   │                  │                  │                │              │
  │<────────────────┤                  │                  │                │              │
  │                  │                  │                  │                │              │
  │ 13. Select User  │                  │                  │                │              │
  │ Click Update     │                  │                  │                │              │
  ├────────────────>│                  │                  │                │              │
  │ (See Update Seq  │                  │                  │                │              │
  │  Diagram Above)  │                  │                  │                │              │
  │                  │                  │                  │                │              │
```

---

## 8. Error Handling Flow - Complete View

### Error Propagation Through Layers

```
Frontend Layer       Boundary Layer          Control Layer           Entity Layer
    │                    │                        │                       │
    │ HTTP Request       │                        │                       │
    ├───────────────────>│                        │                       │
    │                    │ 1. Validate Input      │                       │
    │                    │ ✗ INVALID              │                       │
    │                    │ raise ValueError       │                       │
    │                    │                        │                       │
    │ 2. Catch Exception │                        │                       │
    │ format_error()     │                        │                       │
    │                    │                        │                       │
    │ HTTP 400           │                        │                       │
    │ {success: false,   │                        │                       │
    │  message: "..."}   │                        │                       │
    │<───────────────────┤                        │                       │
    │                    │                        │                       │
    ├─────────────────────────────────────────────────────────────────────┤
    │                    │                        │                       │
    │                    │ Call Control Layer     │                       │
    │                    ├───────────────────────>│                       │
    │                    │                        │ 3. Execute Business   │
    │                    │                        │ Logic ✗ ERROR         │
    │                    │                        │ (e.g., user not found)│
    │                    │                        │ raise NotFoundException
    │                    │                        │                       │
    │                    │ 4. Catch Exception     │                       │
    │                    │ map_error()            │                       │
    │                    │<───────────────────────┤                       │
    │                    │                        │                       │
    │ HTTP 404           │                        │                       │
    │ {success: false,   │                        │                       │
    │  message: "..."}   │                        │                       │
    │<───────────────────┤                        │                       │
    │                    │                        │                       │
    ├─────────────────────────────────────────────────────────────────────┤
    │                    │                        │                       │
    │                    │                        │ 5. DB Query           │
    │                    │                        ├──────────────────────>│
    │                    │                        │ SQL EXECUTE           │
    │                    │                        │ ✗ ERROR (FK violation)
    │                    │                        │                       │
    │                    │                        │ 6. Catch Exception    │
    │                    │                        │ raise IntegrityError  │
    │                    │                        │                       │
    │                    │ 7. Catch Exception     │                       │
    │                    │ map_db_error()         │                       │
    │                    │<────────────────────────────────────────────────│
    │                    │                        │                       │
    │ HTTP 409           │                        │                       │
    │ {success: false,   │                        │                       │
    │  message:          │                        │                       │
    │  "Integrity Error"}│                        │                       │
    │<───────────────────┤                        │                       │
    │                    │                        │                       │
    │ Display Error to   │                        │                       │
    │ User               │                        │                       │
    │                    │                        │                       │
```

---

## 9. Concurrent Request Handling

### Multiple Admin Operations

```
Admin 1          Admin 2          Controller          User Entity         Supabase
  │                  │                  │                  │                │
  │ GET Users       │                  │                  │                │
  ├────────────────>│                  │                  │                │
  │                  │                  │                  │                │
  │                  │ UPDATE User      │                  │                │
  │                  ├─────────────────>│                  │                │
  │                  │                  │                  │                │
  │                  │                  │ 1. Lock Resource │                │
  │                  │                  │ (Row-Level Lock) │                │
  │                  │                  ├──────────────────────────────────>│
  │                  │                  │                  │                │
  │                  │                  │ UPDATE users     │                │
  │                  │                  │ SET ... WHERE    │                │
  │                  │                  │ user_id=?        │                │
  │                  │                  │ (LOCKED)         │                │
  │                  │                  │                  │                │
  │ 2. Get Snapshot  │                  │                  │                │
  │<──────────────────────────────────────────────────────>│                │
  │ SELECT * FROM    │                  │                  │                │
  │ users (no lock)  │                  │                  │                │
  │                  │                  │                  │                │
  │                  │                  │ 3. Unlock        │                │
  │                  │                  │ (Commit)         │                │
  │                  │                  │<─────────────────────────────────>│
  │                  │                  │                  │                │
  │ [All Users       │ Success          │                  │                │
  │ Including Old    │ Response         │                  │                │
  │ Values]          │<──────────────────                  │                │
  │<──────────────────                  │                  │                │
  │                  │                  │                  │                │
```

---

## Summary

This sequence diagram documentation provides:

✅ **Complete flow sequences** for all major operations
✅ **Error handling paths** at each layer
✅ **Database interactions** with actual SQL
✅ **Concurrent request handling** patterns
✅ **Cascade delete operations** in detail
✅ **JWT token verification** flows
✅ **Permission checking** at boundaries
✅ **End-to-end user journeys** from UI to database

Use these diagrams to understand the complete interaction patterns between layers!
