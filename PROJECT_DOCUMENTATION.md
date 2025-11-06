# 📚 CSR Application - Complete Project Documentation

**Project:** Community Service Request (CSR) Management System  
**Framework:** Flask (Backend) + Next.js (Frontend)  
**Database:** Supabase (PostgreSQL)  
**Architecture:** BCE (Boundary-Control-Entity) Pattern  
**Date:** November 2025

---

## 📑 Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Project Architecture](#project-architecture)
3. [Database Schema](#database-schema)
4. [API Reference](#api-reference)
5. [Authentication System](#authentication-system)
6. [Features Implementation](#features-implementation)
7. [Testing (TDD)](#testing-tdd)
8. [User Stories & Business Logic](#user-stories--business-logic)
9. [Development History](#development-history)
10. [Scripts & Utilities](#scripts--utilities)

---

# 1. Quick Start Guide

## Prerequisites
- Python 3.13+
- Node.js 18+
- Supabase account

## Installation

### Backend Setup
```bash
# Navigate to project folder
cd csr_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Copy environment.env and add your Supabase credentials
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET_KEY=your_secret_key
```

### Frontend Setup
```bash
# Install Node dependencies
npm install

# Configure .env file
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Running the Application

### Start Backend (Flask)
```bash
# From project root
python app.py
# Backend runs on http://localhost:5000
```

### Start Frontend (Next.js)
```bash
# From project root
npm run dev
# Frontend runs on http://localhost:3000 or :3001
```

## Default Login Credentials

**All users have password:** `password123`

| Role | Username | Password |
|------|----------|----------|
| User Admin | admin1 | password123 |
| PIN User | pin_user1 | password123 |
| CSR Rep | csr_rep1 | password123 |
| Platform Manager | platform_mgr1 | password123 |

---

# 2. Project Architecture

## BCE Pattern (Boundary-Control-Entity)

### Architecture Overview
```
┌─────────────────────────────────────────────────┐
│                   CLIENT                         │
│              (Next.js Frontend)                  │
└───────────────────┬─────────────────────────────┘
                    │ HTTP Requests
                    ▼
┌─────────────────────────────────────────────────┐
│              BOUNDARY LAYER                      │
│  • Controllers (HTTP handlers)                   │
│  • Request validation                            │
│  • Response formatting                           │
│  • Input sanitization                            │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│              CONTROL LAYER                       │
│  • Business logic                                │
│  • Data processing                               │
│  • Validation rules                              │
│  • Orchestration                                 │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│              ENTITY LAYER                        │
│  • Database models                               │
│  • Data access                                   │
│  • CRUD operations                               │
│  • Supabase client                               │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│              DATABASE                            │
│            (Supabase/PostgreSQL)                 │
└─────────────────────────────────────────────────┘
```

## Directory Structure
```
csr_app/
├── app.py                      # Main Flask application
├── src/
│   ├── entity/                 # ENTITY Layer
│   │   ├── user.py            # User model & auth
│   │   ├── profile.py         # User profiles
│   │   ├── role.py            # User roles
│   │   ├── request.py         # Service requests
│   │   ├── csr_request.py     # CSR assignments
│   │   ├── shortlist.py       # Shortlist management
│   │   └── supabase_config.py # Database config
│   │
│   ├── controller/             # BOUNDARY + CONTROL Layers
│   │   ├── auth/              # Authentication
│   │   │   └── login_controller.py
│   │   ├── userAccount/       # User management
│   │   ├── userProfile/       # Profile management
│   │   ├── request/           # Request management
│   │   ├── shortlist/         # Shortlist operations
│   │   └── role/              # Role management
│   │
│   └── utils/                  # Utilities
│       ├── validators.py      # Input validation
│       ├── sanitizers.py      # Input sanitization
│       ├── helpers.py         # Helper functions
│       ├── auth_middleware.py # JWT middleware
│       └── image_upload.py    # Image handling
│
├── static/                     # Static files
│   └── uploads/               # Uploaded images
│
├── tests/                      # Test suite (pytest)
│   ├── test_login.py          # Login TDD tests
│   ├── test_app.py            # General tests
│   ├── test_data/             # Test data (JSON)
│   └── README.md              # Test documentation
│
├── src/                        # Frontend (Next.js)
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   └── contexts/              # React contexts
│
└── docs/                       # Documentation
    └── PROJECT_DOCUMENTATION.md  # This file
```

## Key Architectural Principles

### 1. Separation of Concerns
- **Boundary:** HTTP handling, validation, formatting
- **Control:** Business logic, orchestration
- **Entity:** Database access, data models

### 2. Single Responsibility
- Each controller handles one feature
- Each entity manages one database table
- Each utility has one clear purpose

### 3. Dependency Flow
```
Boundary → Control → Entity → Database
(Never: Entity → Control or Control → Boundary)
```

### 4. Security Layers
```
Client Request
    ↓
Input Sanitization (Boundary)
    ↓
Input Validation (Boundary)
    ↓
Authentication Check (Middleware)
    ↓
Authorization Check (Control)
    ↓
Business Logic (Control)
    ↓
Data Access (Entity)
```

---

# 3. Database Schema

## Core Tables

### user_accounts
Primary user authentication table
```sql
CREATE TABLE user_accounts (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- pbkdf2:sha256 hashed
    role_id INTEGER REFERENCES user_roles(role_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### user_profiles
Extended user information
```sql
CREATE TABLE user_profiles (
    profile_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user_accounts(user_id) ON DELETE CASCADE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### user_roles
Role-based access control
```sql
CREATE TABLE user_roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Default Roles
INSERT INTO user_roles (role_id, role_name, description) VALUES
(1, 'User Admin', 'Manages user accounts and profiles'),
(2, 'PIN', 'Person in Need - Creates service requests'),
(3, 'CSR Rep', 'Community Service Representative'),
(4, 'Platform Management', 'Overall platform management');
```

### service_requests
Service requests from PINs
```sql
CREATE TABLE service_requests (
    request_id SERIAL PRIMARY KEY,
    pin_user_id INTEGER REFERENCES user_accounts(user_id),
    service_type_id INTEGER REFERENCES service_types(service_type_id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    priority VARCHAR(20),
    location TEXT,
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### csr_requests
CSR assignments to service requests
```sql
CREATE TABLE csr_requests (
    csr_request_id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES service_requests(request_id) ON DELETE CASCADE,
    csr_user_id INTEGER REFERENCES user_accounts(user_id),
    status VARCHAR(20) DEFAULT 'PENDING',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT
);
```

### service_types
Categories of services
```sql
CREATE TABLE service_types (
    service_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);
```

### shortlist
CSR shortlist for requests
```sql
CREATE TABLE shortlist (
    shortlist_id SERIAL PRIMARY KEY,
    request_id INTEGER REFERENCES service_requests(request_id) ON DELETE CASCADE,
    csr_user_id INTEGER REFERENCES user_accounts(user_id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'PENDING',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);
```

## Entity Relationships

```
user_accounts (1) ──────── (1) user_profiles
      │                             
      │ (1)                         
      │                             
      ├────────── (M) service_requests (PIN creates)
      │                    │
      │                    │ (1)
      │                    │
      │                    ├── (M) csr_requests (CSR assigned)
      │                    │
      │                    └── (M) shortlist (CSR shortlisted)
      │
      └────────── (M) csr_requests (CSR user)
      
user_roles (1) ──────── (M) user_accounts
service_types (1) ─────── (M) service_requests
```

---

# 4. API Reference

## Authentication Endpoints

### POST /api/auth/login
User login with credentials

**Request:**
```json
{
  "username": "admin1",
  "password": "password123",
  "role_name": "User Admin"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 1,
    "username": "admin1",
    "role": "User Admin",
    "role_id": 1
  }
}
```

**Error (401):**
```json
{
  "success": false,
  "message": "Invalid username or password"
}
```

### POST /api/auth/logout
Invalidate user session

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### GET /api/auth/verify
Verify token validity

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "valid": true,
  "user": {
    "user_id": 1,
    "username": "admin1",
    "role": "User Admin"
  }
}
```

## User Account Endpoints

### GET /api/userAccount
List all user accounts

**Response (200):**
```json
{
  "success": true,
  "users": [
    {
      "user_id": 1,
      "username": "admin1",
      "role_id": 1,
      "role_name": "User Admin",
      "is_active": true,
      "created_at": "2025-11-01T10:00:00"
    }
  ]
}
```

### POST /api/userAccount
Create new user account

**Request:**
```json
{
  "username": "newuser",
  "password": "password123",
  "role_id": 2
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User account created successfully",
  "user_id": 10
}
```

### PUT /api/userAccount/<user_id>
Update user account

**Request:**
```json
{
  "username": "updateduser",
  "role_id": 3,
  "is_active": true
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "User account updated successfully"
}
```

### PUT /api/userAccount/<user_id>/suspend
Suspend/activate user account

**Request:**
```json
{
  "is_active": false
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "User account suspended successfully"
}
```

## User Profile Endpoints

### GET /api/userProfile
Get all user profiles

### GET /api/userProfile/<profile_id>
Get specific user profile

### POST /api/userProfile
Create user profile

### PUT /api/userProfile/<profile_id>
Update user profile

## Service Request Endpoints

### GET /api/requests
List service requests

**Query Parameters:**
- `status`: ACTIVE, SUSPENDED, FULFILLED
- `service_type_id`: Filter by service type
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 10)

**Response (200):**
```json
{
  "success": true,
  "requests": [
    {
      "request_id": 1,
      "title": "Need food assistance",
      "description": "Family needs food support",
      "status": "ACTIVE",
      "service_type": "Food Aid",
      "pin_username": "pin_user1",
      "created_at": "2025-11-01T10:00:00",
      "image_path": "/static/uploads/requests/image.jpg"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25
  }
}
```

### POST /api/requests
Create new service request

**Request (multipart/form-data):**
```
title: "Need medical assistance"
description: "Require medication support"
service_type_id: 2
priority: "HIGH"
location: "123 Main St"
image: <file>
```

**Response (201):**
```json
{
  "success": true,
  "message": "Request created successfully",
  "request_id": 15
}
```

### PUT /api/requests/<request_id>
Update service request

### DELETE /api/requests/<request_id>
Delete service request

### GET /api/requests/service-types
Get all service types

**Response (200):**
```json
{
  "success": true,
  "service_types": [
    {"service_type_id": 1, "type_name": "Food Aid"},
    {"service_type_id": 2, "type_name": "Medical Support"},
    {"service_type_id": 3, "type_name": "Housing Assistance"}
  ]
}
```

## Shortlist Endpoints

### GET /api/shortlist
Get user's shortlist

### POST /api/shortlist
Add request to shortlist

**Request:**
```json
{
  "request_id": 5
}
```

### DELETE /api/shortlist/<shortlist_id>
Remove from shortlist

### GET /api/shortlist/stats
Get shortlist statistics

---

# 5. Authentication System

## Password Hashing

**Algorithm:** pbkdf2:sha256  
**Library:** werkzeug.security  
**Format:** `pbkdf2:sha256:260000$salt$hash`

### Implementation
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash password
hashed = generate_password_hash(password, method='pbkdf2:sha256')

# Verify password
is_valid = check_password_hash(stored_hash, provided_password)
```

## JWT Tokens

**Library:** PyJWT  
**Algorithm:** HS256  
**Expiration:** 24 hours

### Token Structure
```json
{
  "user_id": 1,
  "username": "admin1",
  "role": "User Admin",
  "role_id": 1,
  "exp": 1699401600
}
```

### Token Flow
```
1. User logs in with credentials
2. Server validates username/password
3. Server generates JWT token
4. Token sent to client
5. Client stores token (localStorage)
6. Client sends token in Authorization header
7. Server validates token on each request
8. Token expires after 24 hours
```

## Security Features

### 1. Input Sanitization
```python
# Username sanitization
username = Sanitizers.sanitize_username(raw_username)
# Removes special characters, enforces length

# String sanitization
text = Sanitizers.sanitize_string(raw_text)
# Removes HTML tags, trims whitespace
```

### 2. Input Validation
```python
# Email validation
is_valid = Validators.validate_email(email)

# Phone validation
is_valid = Validators.validate_phone(phone)

# Required fields validation
is_valid, error_msg, missing = RequestHelpers.validate_required_fields(
    data, ['username', 'password', 'role_name']
)
```

### 3. SQL Injection Protection
- Supabase client uses parameterized queries
- No raw SQL concatenation
- ORM-style query building

### 4. XSS Protection
- Input sanitization removes HTML tags
- Frontend escapes user content
- CSP headers configured

### 5. CORS Configuration
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

# 6. Features Implementation

## User Management

### Create User Account
**Who:** User Admin  
**Feature:** Create new user with role assignment  
**Validation:**
- Username uniqueness
- Password strength
- Valid role_id
- Required fields

**Business Logic:**
```python
def create_user(username, password, role_id):
    # 1. Validate inputs
    # 2. Check username uniqueness
    # 3. Hash password
    # 4. Insert into database
    # 5. Create default profile
    # 6. Log activity
    # 7. Return user_id
```

### Update User Account
**Who:** User Admin  
**Feature:** Modify username, role, or status  
**Validation:**
- User exists
- New username not taken (if changed)
- Valid role_id

### Suspend/Activate Account
**Who:** User Admin  
**Feature:** Toggle user active status  
**Effect:**
- Suspended users cannot login
- Existing sessions invalidated
- Data preserved (soft delete)

## Service Request Management

### Create Request
**Who:** PIN User  
**Feature:** Submit service request with optional image  
**Validation:**
- Title required (max 200 chars)
- Description optional
- Valid service_type_id
- Image size < 5MB
- Image formats: jpg, jpeg, png, gif

**Image Upload:**
```python
# Upload folder: static/uploads/requests/
# Filename format: {timestamp}_{random_hex}.{ext}
# Example: 1699401600_a1b2c3d4.jpg
```

### Update Request Status
**Who:** PIN User, CSR Rep  
**Feature:** Change request status  
**Statuses:**
- ACTIVE - Open for assignment
- SUSPENDED - Temporarily paused
- FULFILLED - Completed

### Search & Filter Requests
**Filters:**
- Status (ACTIVE, SUSPENDED, FULFILLED)
- Service type
- Date range
- Location
- Priority

## CSR Assignment System

### Shortlist Process
```
1. CSR Rep views available requests
2. CSR adds interesting requests to shortlist
3. CSR reviews shortlist
4. CSR applies for selected requests
5. PIN reviews applications
6. PIN assigns CSR to request
7. CSR completes service
8. PIN marks as fulfilled
```

### Assignment Logic
```python
def assign_csr_to_request(request_id, csr_user_id):
    # 1. Verify request is ACTIVE
    # 2. Verify CSR is eligible
    # 3. Check for conflicts
    # 4. Create csr_request record
    # 5. Update request status
    # 6. Notify PIN and CSR
    # 7. Log activity
```

---

# 7. Testing (TDD)

## Test Framework
**Framework:** pytest  
**Coverage:** Login feature (comprehensive)  
**Test Data:** JSON files

## Test Structure
```
tests/
├── __init__.py
├── test_login.py              # Login TDD tests
├── test_app.py                # General app tests
├── test_cascade_delete.py     # Database tests
├── test_data/
│   └── login_test_cases.json  # Test scenarios
└── README.md                   # Test documentation
```

## Running Tests

### All Tests
```bash
pytest
```

### Login Tests Only
```bash
pytest tests/test_login.py -v
```

### Specific Test
```bash
pytest tests/test_login.py::test_valid_logins -v
```

### With Coverage
```bash
pytest --cov=src --cov-report=html
```

## Test Categories

### 1. Valid Login Tests (4 scenarios)
- Admin login with correct credentials
- PIN user login
- CSR Rep login
- Platform Manager login

### 2. Invalid Login Tests (6 scenarios)
- Wrong password
- Non-existent username
- Empty username
- Empty password
- Missing username field
- Missing password field

### 3. Security Tests (3 scenarios)
- SQL injection attempts
- XSS attack attempts
- Case-sensitive username validation

### 4. Token Tests
- JWT format validation
- Token presence verification
- User ID in response

### 5. Response Format Tests
- Success response structure
- Error response structure
- Required fields validation

## Test Data Format (JSON)
```json
{
  "valid_logins": [
    {
      "test_name": "admin_login_success",
      "username": "admin1",
      "password": "password123",
      "expected_status": 200,
      "expected_role": "User Admin",
      "description": "Admin user should login successfully"
    }
  ]
}
```

---

# 8. User Stories & Business Logic

## User Admin Stories

### US1: Create User Account
**As a** User Admin  
**I want to** create new user accounts  
**So that** new users can access the system

**Acceptance Criteria:**
- [x] Username must be unique
- [x] Password must be hashed
- [x] Role must be assigned
- [x] Default profile created
- [x] Activity logged

**Business Rules:**
- Username: 3-50 characters, alphanumeric + underscore
- Password: Minimum 8 characters
- Role: Must be valid role_id from user_roles table
- Email: Must be valid format if provided
- Phone: Must be valid format if provided

### US2: View All User Accounts
**As a** User Admin  
**I want to** view all user accounts  
**So that** I can manage users

**Acceptance Criteria:**
- [x] List all users with their roles
- [x] Show active/inactive status
- [x] Include creation date
- [x] Searchable and filterable

### US3: Update User Account
**As a** User Admin  
**I want to** update user information  
**So that** I can keep records current

**Acceptance Criteria:**
- [x] Can change username (if not taken)
- [x] Can change role
- [x] Can update profile information
- [x] Cannot change password (separate feature)

### US4: Suspend/Activate Account
**As a** User Admin  
**I want to** suspend or activate user accounts  
**So that** I can control access

**Acceptance Criteria:**
- [x] Toggle active status
- [x] Suspended users cannot login
- [x] Data is preserved
- [x] Can be reactivated

## PIN User Stories

### US5: Create Service Request
**As a** PIN User  
**I want to** submit service requests  
**So that** I can get community support

**Acceptance Criteria:**
- [x] Provide title and description
- [x] Select service type
- [x] Upload optional image
- [x] Set priority level
- [x] Specify location

**Business Rules:**
- Title: Required, max 200 characters
- Description: Optional, max 2000 characters
- Image: Max 5MB, formats: jpg, jpeg, png, gif
- Service type: Must exist in service_types table
- Priority: LOW, MEDIUM, HIGH
- Status: Defaults to ACTIVE

### US6: View My Requests
**As a** PIN User  
**I want to** view my submitted requests  
**So that** I can track their status

**Acceptance Criteria:**
- [x] See all my requests
- [x] Filter by status
- [x] Sort by date
- [x] View assigned CSRs

### US7: Update Request
**As a** PIN User  
**I want to** update my requests  
**So that** I can correct or add information

**Acceptance Criteria:**
- [x] Edit title, description
- [x] Change service type
- [x] Update priority
- [x] Upload new image
- [x] Cannot edit if FULFILLED

### US8: Mark Request as Fulfilled
**As a** PIN User  
**I want to** mark requests as fulfilled  
**So that** CSRs know it's completed

**Acceptance Criteria:**
- [x] Change status to FULFILLED
- [x] Cannot be undone
- [x] Notify assigned CSR
- [x] Archive request

## CSR Representative Stories

### US9: View Available Requests
**As a** CSR Rep  
**I want to** view all active requests  
**So that** I can find opportunities to help

**Acceptance Criteria:**
- [x] See ACTIVE requests only
- [x] Filter by service type
- [x] Filter by location
- [x] Sort by priority/date

### US10: Add to Shortlist
**As a** CSR Rep  
**I want to** add requests to my shortlist  
**So that** I can review them later

**Acceptance Criteria:**
- [x] Add any ACTIVE request
- [x] View my shortlist
- [x] Remove from shortlist
- [x] Apply from shortlist

### US11: Apply for Request
**As a** CSR Rep  
**I want to** apply to help with requests  
**So that** I can provide service

**Acceptance Criteria:**
- [x] Submit application
- [x] Include notes/message
- [x] Wait for PIN approval
- [x] Get notification

### US12: View Assigned Requests
**As a** CSR Rep  
**I want to** see requests assigned to me  
**So that** I can fulfill them

**Acceptance Criteria:**
- [x] List of assigned requests
- [x] See PIN contact info
- [x] Mark as in-progress
- [x] Update status

## Platform Management Stories

### US13: View System Analytics
**As a** Platform Manager  
**I want to** view system statistics  
**So that** I can monitor platform health

**Acceptance Criteria:**
- [ ] Total users by role
- [ ] Active vs inactive users
- [ ] Request statistics
- [ ] Fulfillment rate
- [ ] CSR performance metrics

### US14: Manage Service Types
**As a** Platform Manager  
**I want to** add/edit service types  
**So that** the system stays relevant

**Acceptance Criteria:**
- [x] Create new service types
- [x] Edit existing types
- [x] Deactivate types
- [x] View usage statistics

---

# 9. Development History

## November 6, 2025 - Major Cleanup & TDD Implementation

### What Was Done
1. **Fixed Login Issue**
   - Problem: scrypt hashing required cryptography library
   - Solution: Migrated to pbkdf2:sha256 (built into werkzeug)
   - Result: All 36 users can login with password123

2. **Created TDD Tests**
   - Added `tests/test_login.py` with 17+ test cases
   - Created `tests/test_data/login_test_cases.json`
   - Comprehensive coverage: valid, invalid, security tests

3. **Cleaned Up Scripts**
   - Deleted 40+ unnecessary scripts
   - Kept only essential utilities
   - Organized test suite properly

4. **Standardized Passwords**
   - All 36 users now use: `password123`
   - Properly hashed with pbkdf2:sha256
   - Verified in database

## Previous Development Milestones

### Authentication System
- Implemented JWT-based authentication
- Role-based access control (RBAC)
- Session management
- Token invalidation on logout

### User Management
- User account CRUD operations
- User profile management
- Role assignment
- Account suspension/activation

### Request Management
- Service request creation
- Image upload functionality
- Status management
- Search and filtering

### CSR Assignment
- Shortlist functionality
- Application process
- Assignment workflow
- Status tracking

### Database Design
- Normalized schema
- Foreign key constraints
- Cascade delete rules
- Indexes for performance

### BCE Architecture
- Clear layer separation
- Boundary: Controllers
- Control: Business logic
- Entity: Database access

---

# 10. Scripts & Utilities

## Essential Scripts (Keep)

### `app.py`
Main Flask application entry point
```bash
python app.py
```

### `refresh_db.py`
Reset database with fresh test data
```bash
python refresh_db.py
```

### `reset_all_passwords.py`
Reset all user passwords to standard value
```bash
python reset_all_passwords.py
```

### `show_active_users.py`
Display all active users in database
```bash
python show_active_users.py
```

### `preflight_check.py`
System health check before deployment
```bash
python preflight_check.py
```

### `check_db_schema.py`
Verify database schema integrity
```bash
python check_db_schema.py
```

## Test Suite Scripts

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_login.py -v
```

### Run with Coverage Report
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

# Appendix: Quick Reference

## Common Commands

### Start Development Servers
```bash
# Backend
python app.py

# Frontend
npm run dev
```

### Database Operations
```bash
# Reset database
python refresh_db.py

# Reset passwords
python reset_all_passwords.py

# View users
python show_active_users.py
```

### Testing
```bash
# All tests
pytest

# Login tests only
pytest tests/test_login.py -v

# Specific test
pytest tests/test_login.py::test_valid_logins
```

## Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME=CSR Application
```

## API Base URLs

- **Development Backend:** http://localhost:5000
- **Development Frontend:** http://localhost:3000 or :3001

## Default Credentials

**All passwords:** `password123`

- **Admin:** admin1
- **PIN:** pin_user1
- **CSR:** csr_rep1
- **Platform:** platform_mgr1

---

**End of Documentation**

For issues or questions, refer to individual feature documentation or check the test suite for expected behavior.
