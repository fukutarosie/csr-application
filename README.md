# 🚀 CSR Application - Complete Setup Guide

**Customer Service Request Management System**

**Last Updated:** November 6, 2025  
**Latest:** ✅ Create User Bug Fixed - Admin Dashboard Fully Operational

A professional full-stack application built with:
- **Backend:** Flask (Python) + Supabase PostgreSQL
- **Frontend:** Next.js 14 (React) + Tailwind CSS
- **Architecture:** Boundary-Control-Entity (BCE) Pattern

---

## 🎉 Recent Updates (November 6, 2025)

### ✅ Critical Bug Fix - Create User Endpoint
- **Issue:** Create user functionality returned HTTP 500
- **Fix:** Corrected helper class import (DataHelpers vs ResponseHelpers)
- **Status:** Fully operational
- **Details:** See [BUGFIX_NOV_6_2025.md](BUGFIX_NOV_6_2025.md)

### ✅ Admin Dashboard Features
- View all users ✅
- Create new users ✅ **FIXED**
- Search users ✅
- Edit users ✅
- Suspend/Activate users ✅
- Manage user profiles (roles) ✅

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Installation Guide](#installation-guide)
4. [Project Structure](#project-structure)
5. [Features & Architecture](#features--architecture)
6. [Input Validation & Security](#input-validation--security)
7. [Running the Application](#running-the-application)
8. [API Endpoints](#api-endpoints)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)
11. [Documentation](#documentation)

---

## ⚡ Quick Start

**For the impatient developer (Windows):**

```bash
# Option 1: Batch file (automatic setup)
run.bat

# Option 2: PowerShell script
.\run.ps1

# Option 3: Manual
python app.py              # Terminal 1
npm run dev               # Terminal 2
# Visit http://localhost:3000
```

**For macOS/Linux:**

```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend
npm run dev
```

---

## 📦 Prerequisites

**Required:**
- ✅ Python 3.8 or higher
- ✅ Node.js 14 or higher (with npm)
- ✅ Git (for version control)
- ✅ Supabase account (free tier available)

**Optional but Recommended:**
- 🔧 Virtual environment tool (venv built into Python)
- 💻 VS Code or similar IDE
- 📮 Postman (for API testing)

**Check Your Versions:**

```bash
python --version          # Should be 3.8+
node --version           # Should be 14+
npm --version            # Should be 6.0+
git --version            # For version control
```

---

## 🔧 Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/fukutarosie/csr-application.git
cd csr-application
```

### Step 2: Backend Setup (Flask + Python)

#### 2a. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

After activation, your terminal prompt should show `(venv)` at the beginning.

#### 2b. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Flask: Web framework
- flask-cors: Cross-origin support
- python-dotenv: Environment variable management
- PyJWT: JWT token handling
- supabase-py: Supabase client
- werkzeug: Password hashing

#### 2c. Configure Environment Variables

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your Supabase credentials:**
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-public-key
   
   # Flask Configuration
   FLASK_APP=app.py
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key-here
   
   # JWT Configuration
   JWT_SECRET_KEY=your-jwt-secret-key
   JWT_ACCESS_TOKEN_EXPIRES=3600
   
   # CORS Configuration
   CORS_ORIGINS=http://localhost:3000
   ```

3. **Get your Supabase credentials:**
   - Go to [supabase.com](https://supabase.com)
   - Open your project → Settings → API
   - Copy `URL` → `SUPABASE_URL`
   - Copy `public (anon)` key → `SUPABASE_KEY`

#### 2d. Verify Backend Setup

```bash
# Test Flask import
python -c "from app import app; print('[OK] Flask app loaded successfully')"

# Expected output: [OK] Flask app loaded successfully
```

---

### Step 3: Frontend Setup (Next.js + React)

#### 3a. Install Node Dependencies

```bash
npm install
```

Or with yarn:
```bash
yarn install
```

**What gets installed:**
- next: React framework
- react: UI library
- axios: HTTP client
- tailwindcss: CSS framework
- And many other tools

#### 3b. Verify Frontend Setup

```bash
# Test Next.js build
npm run build

# Expected: "✓ Compiled successfully"
```

---

## 📁 Project Structure

```
csr-application/
│
├── 📂 src/
│   ├── 📂 app/                          # Next.js Frontend (React Pages)
│   │   ├── page.js                      # Login page
│   │   ├── admin/page.js                # Admin dashboard
│   │   ├── csr/page.js                  # CSR dashboard
│   │   ├── pin/page.js                  # PIN dashboard
│   │   ├── platform/page.js             # Platform dashboard
│   │   ├── layout.js                    # Root layout wrapper
│   │   └── globals.css                  # Global styles
│   │
│   ├── 📂 config/
│   │   └── supabase.py                  # Supabase config (backwards compat)
│   │
│   ├── 📂 controller/                   # BOUNDARY LAYER (HTTP Handlers)
│   │   ├── 📂 auth/
│   │   │   ├── auth_middleware.py       # JWT verification
│   │   │   ├── auth_controller.py       # Authentication logic
│   │   │   ├── login_controller.py      # Login endpoint
│   │   │   └── logout_controller.py     # Logout endpoint
│   │   │
│   │   ├── 📂 userAccount/
│   │   │   ├── create_user_account_controller.py
│   │   │   ├── view_user_account_controller.py
│   │   │   ├── update_user_account_controller.py
│   │   │   ├── suspend_user_account_controller.py
│   │   │   └── search_user_account_controller.py
│   │   │
│   │   └── 📂 userProfile/
│   │       ├── create_user_profile_controller.py
│   │       ├── view_user_profile_controller.py
│   │       ├── update_user_profile_controller.py
│   │       ├── suspend_user_profile_controller.py
│   │       └── search_user_profile_controller.py
│   │
│   └── 📂 entity/                       # CONTROL + ENTITY LAYER (Business Logic)
│       ├── supabase_config.py           # Database configuration (NEW)
│       ├── user.py                      # User entity & business logic
│       ├── role.py                      # Role entity & business logic
│       ├── profile.py                   # Profile entity & business logic
│       ├── request.py                   # Request entity
│       ├── csr_request.py               # CSR request entity
│       └── __init__.py                  # Entity exports
│
├── 📂 tests/                            # Test Suite
│   ├── test_all_cruds.py                # CRUD operations test
│   ├── test_cascade_delete.py           # CASCADE DELETE test
│   └── test_password.py                 # Password verification test
│
├── 📂 utilities/                        # Maintenance Scripts
│   ├── check_db_schema.py               # Database schema inspection
│   ├── check_passwords.py               # Password hash inspection
│   └── fix_passwords.py                 # Password update utility
│
├── 📄 app.py                            # Flask application entry point
├── 📄 requirements.txt                  # Python dependencies
├── 📄 package.json                      # Node.js dependencies
├── 📄 .env                              # Environment variables (local, gitignored)
├── 📄 .env.example                      # Environment template
├── 📄 .gitignore                        # Git ignore rules
│
└── 📄 Documentation Files:
    ├── README.md                        # This file
    ├── BCE_ARCHITECTURE_GUIDE.md        # Detailed architecture explanation
    ├── BCE_ARCHITECTURE_DIAGRAMS.md     # Visual diagrams & flows
    ├── LOGIN_FLOW_DETAILED.md           # Login use case deep dive
    ├── API_QUICK_REFERENCE.md           # API endpoint reference
    ├── MODULAR_CONTROLLER_ARCHITECTURE.md
    ├── CONTROLLER_REFACTORING_COMPLETE.md
    ├── PROJECT_RESTRUCTURING.md         # Restructuring changelog
    └── QUICKSTART.md                    # Quick reference
```

---

## 🎯 Features & Architecture

### ✨ Key Features

✅ **Authentication & Authorization**
- Secure login/logout with JWT tokens
- Role-based access control (4 user roles)
- Protected API endpoints with middleware
- Session management

✅ **User Management**
- Create/Read/Update/Delete (CRUD) user accounts
- Suspend/Activate user accounts
- Search users by criteria
- Role assignment

✅ **Profile/Role Management**
- Create and manage user profiles
- Role-based permissions
- CASCADE DELETE: Auto-delete users when role deleted
- Search profiles

✅ **User Roles**
| Role | Description | Permissions |
|------|-------------|------------|
| **User Admin** | System administrator | Full user management |
| **PIN** | Partner Info Network | View requests, manage partners |
| **CSR Rep** | Customer Service | Handle customer requests |
| **Platform Mgmt** | Platform administration | Platform-level access |

### 🏗️ Architecture Pattern: Boundary-Control-Entity (BCE)

The application follows the **BCE pattern** for clean architecture:

```
HTTP Request
    ↓
┌─────────────────────────┐
│ BOUNDARY (Controllers)  │  ← HTTP validation, response formatting
│ src/controller/*        │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ CONTROL (Business Logic)│  ← Business rules, validations
│ src/entity/*.py methods │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ ENTITY (Persistence)    │  ← Database operations
│ src/entity/*.py DB calls│
└────────────┬────────────┘
             ↓
        DATABASE
       (Supabase)
```

**Benefits:**
✓ Clean separation of concerns
✓ Easy to test and maintain
✓ Reusable business logic
✓ Consistent error handling

**📖 See:** `BCE_ARCHITECTURE_GUIDE.md` for detailed explanation

---

## 🚀 Running the Application

### Option 1: Automatic Setup (Windows - Easiest)

```bash
# Run the batch file
run.bat

# Or PowerShell script
.\run.ps1
```

This automatically:
- Creates Python virtual environment
- Installs all dependencies
- Starts Flask backend on port 5000
- Starts Next.js frontend on port 3000

### Option 2: Manual Setup (All Platforms)

**Terminal 1 - Backend:**
```bash
# Activate virtual environment first
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start Flask
python app.py

# Expected output:
# WARNING: This is a development server...
# Running on http://127.0.0.1:5000
```

**Terminal 2 - Frontend:**
```bash
# In the project root
npm run dev

# Expected output:
# ▲ Next.js 14.2.33
# - Local:        http://localhost:3000
# ✓ Ready in X.XXs
```

**Terminal 3 - Optional: Run Tests**
```bash
python tests/test_all_cruds.py
python tests/test_cascade_delete.py
```

### Access the Application

📍 **Frontend:** http://localhost:3000
📍 **Backend API:** http://localhost:5000
📍 **API Documentation:** See section below

---

## 📡 API Endpoints

### Authentication

```
POST   /api/auth/login         Login with credentials
POST   /api/auth/logout        Logout and invalidate token
```

**Login Example:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin1",
    "password": "password123",
    "role_name": "User Admin"
  }'
```

### User Account Management

```
GET    /api/userAccount        Get all users
POST   /api/userAccount        Create new user
GET    /api/userAccount/<id>   Get specific user
PUT    /api/userAccount/<id>   Update user
PUT    /api/userAccount/<id>/suspend     Suspend user
PUT    /api/userAccount/<id>/activate    Activate user
DELETE /api/userAccount/<id>/delete      Delete user
POST   /api/userAccount/search Search users
```

### User Profile Management

```
GET    /api/userProfile        Get all profiles
POST   /api/userProfile        Create new profile
GET    /api/userProfile/<id>   Get specific profile
PUT    /api/userProfile/<id>   Update profile
DELETE /api/userProfile/<id>/delete      Delete profile
POST   /api/userProfile/search Search profiles
```

**📖 See:** `API_QUICK_REFERENCE.md` for detailed endpoint documentation

---

## 🔒 Input Validation & Security

### Comprehensive Input Validation

All user input is validated in the BOUNDARY layer before processing:

#### **Email Validation**
- ✅ Valid email format (must have @ and domain)
- ✅ Maximum 100 characters
- ✅ Uniqueness check (no duplicate emails)

#### **Username Validation**
- ✅ 3-20 characters
- ✅ Alphanumeric + hyphens/underscores only
- ✅ Uniqueness check (no duplicate usernames)

#### **Password Validation**
- ✅ Minimum 8 characters
- ✅ Must contain uppercase letter (A-Z)
- ✅ Must contain lowercase letter (a-z)
- ✅ Must contain digit (0-9)

#### **Full Name Validation**
- ✅ 2-100 characters
- ✅ Must contain letters

#### **Phone Validation**
- ✅ Minimum 10 digits
- ✅ Supports standard phone formats

#### **JSON & Request Validation**
- ✅ Valid JSON format check
- ✅ Required fields presence
- ✅ Empty body detection
- ✅ Authorization header validation

### Security Features

✅ **Input Sanitization**
- All user input cleaned and normalized
- Extra whitespace removed
- HTML characters escaped
- SQL injection prevention

✅ **Token Security**
- JWT token format validation
- Token expiration checking
- Bearer token format verification
- Session token invalidation on logout

✅ **Error Handling**
- Specific error codes for each failure type
- Secure error messages (no database details leaked)
- Proper HTTP status codes (400, 401, 404, 409, 500)

✅ **Audit Logging**
- All authentication events logged
- User profile updates tracked
- Activity timestamps recorded

### Validation Files

📄 **`src/utils/validators.py`** - All validation logic (250+ lines)
- `Validators` class: 9 validation methods
- `ProfileValidators` class: 3 profile-specific methods

📄 **`src/utils/sanitizers.py`** - Input sanitization (180+ lines)
- `Sanitizers` class: 9 sanitization methods

📄 **`src/utils/helpers.py`** - Controller helpers (400+ lines)
- `TokenHelpers`: Token extraction & validation
- `RequestHelpers`: JSON & field validation
- `ResponseHelpers`: Standardized responses
- `DataHelpers`: Data formatting & filtering
- `PaginationHelpers`: Pagination support

📄 **`VALIDATION_SUMMARY.md`** - Complete validation reference with examples

---

## ✅ Testing

### Run All CRUD Tests

```bash
# Comprehensive test of all operations
python tests/test_all_cruds.py

# Expected: [OK] ALL TESTS PASSED!
```

### Test CASCADE DELETE

```bash
# Verify CASCADE DELETE constraint works
python tests/test_cascade_delete.py

# Expected: [OK] CASCADE DELETE VERIFIED!
```

### Test Passwords

```bash
# Verify password validation
python tests/test_password.py
```

### Check Database Schema

```bash
# Inspect database tables and structure
python utilities/check_db_schema.py
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `Port 5000 already in use`
```bash
# Windows: Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :5000
kill -9 <PID>
```

**Problem:** `ModuleNotFoundError: No module named 'flask'`
```bash
# Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**Problem:** `Supabase connection error`
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check internet connection
- Verify Supabase project is active

### Frontend Issues

**Problem:** `npm ERR! code ENOENT`
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem:** `NEXT_PUBLIC_API_URL` not working
- Ensure backend is running on port 5000
- Check `.env` configuration
- Clear browser cache (Ctrl+Shift+Delete)

### Database Issues

**Problem:** `relations do not exist` error
```bash
# Tables not created in Supabase
# Navigate to Supabase Dashboard → SQL Editor
# Create tables manually or run migration script
```

**Problem:** `Foreign key constraint violation`
- Ensure CASCADE DELETE is configured
- Check referential integrity
- Run: `python utilities/check_db_schema.py`

---

## 📚 Documentation

### In-Depth Guides

For deeper understanding of the system architecture and design patterns, refer to these documentation files:

- **[BCE_ARCHITECTURE_GUIDE.md](./BCE_ARCHITECTURE_GUIDE.md)** 📖
  - Comprehensive Boundary-Control-Entity architecture explanation
  - All 10 use cases with detailed layer breakdown
  - Error handling patterns and best practices
  - File organization reference
  - ~1000+ lines of detailed explanation

- **[BCE_ARCHITECTURE_DIAGRAMS.md](./BCE_ARCHITECTURE_DIAGRAMS.md)** 📊
  - Visual ASCII flow diagrams for all major operations
  - Complete flow from HTTP request to database response
  - Error handling flow charts
  - Controller file organization diagram
  - 9 different flow diagrams

- **[PROJECT_RESTRUCTURING.md](./PROJECT_RESTRUCTURING.md)** 🔄
  - Explanation of recent project reorganization
  - Before/after file structure comparison
  - Import path changes and benefits
  - Test and utility directory organization

- **[API_QUICK_REFERENCE.md](./API_QUICK_REFERENCE.md)** ⚡
  - Quick lookup for all API endpoints
  - Request/response examples
  - Authentication details
  - Error codes and responses

- **[LOGIN_FLOW_DETAILED.md](./LOGIN_FLOW_DETAILED.md)** 🔐
  - Deep dive into the login authentication flow
  - JWT token generation and verification
  - Session management
  - Security considerations

- **[ADMIN_DASHBOARD_GUIDE.md](./ADMIN_DASHBOARD_GUIDE.md)** 👨‍💼
  - How to use the admin dashboard
  - User management features
  - Profile management
  - Search and filter operations

- **[VALIDATION_SUMMARY.md](./VALIDATION_SUMMARY.md)** 🔒
  - Complete input validation reference
  - All validation methods documented
  - Error codes and HTTP status codes
  - Validation examples and flow diagrams

- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** ⚡
  - Quick lookup for validators, sanitizers, helpers
  - Copy-paste ready import statements
  - Common validation patterns
  - Best practices checklist

- **[CONTROLLER_IMPROVEMENTS_GUIDE.md](./CONTROLLER_IMPROVEMENTS_GUIDE.md)** 📚
  - Detailed guide to all utility modules
  - Enhanced controller patterns
  - Enhanced entity methods
  - Data validation flow diagrams

- **[IMPROVEMENTS_SUMMARY.md](./IMPROVEMENTS_SUMMARY.md)** 📊
  - Summary of all improvements
  - Benefits overview
  - Files created/modified inventory
  - Next steps checklist

- **[HOW_JSON_AND_WEB_WORKS.md](./HOW_JSON_AND_WEB_WORKS.md)** 🌐
  - Comprehensive JSON explanation
  - Web request/response cycle
  - HTTP methods and status codes
  - Real examples from your app

---

## 🔐 Security

### Best Practices Implemented

✅ **Password Security**
- Passwords hashed using Werkzeug security
- Never stored in plain text
- Validated on login

✅ **Authentication**
- JWT tokens with expiration
- Role-based access control
- Middleware protection on protected endpoints

✅ **Database**
- CASCADE DELETE for referential integrity
- Foreign key constraints
- SQL injection prevention with parameterized queries

✅ **API Security**
- CORS enabled for frontend only
- Input validation on all endpoints
- Proper error handling without exposing internals

### Environment Security

Never commit sensitive data:
```bash
# Automatically ignored by .gitignore:
.env
.env.local
__pycache__/
node_modules/
.next/
venv/
```

---

## 🤝 Contributing

### Development Guidelines

1. **Follow the BCE Pattern**
   - Controllers (Boundary) handle HTTP
   - Entity methods handle business logic
   - Keep concerns separated

2. **Add Tests**
   - Create tests in `tests/` directory
   - Run `python tests/test_all_cruds.py` before pushing
   - Ensure new features have test coverage

3. **Update Documentation**
   - Update relevant `.md` files
   - Keep API documentation current
   - Add flowcharts for new features

4. **Commit Messages**
   - Use clear, descriptive messages
   - Reference feature number if applicable
   - Example: `add user suspension feature for admin role`

---

## 📞 Support & Contact

- **Project Repository:** https://github.com/fukutarosie/csr-application
- **Issues:** Create an issue on GitHub
- **Documentation:** See documentation files in root directory
- **Team:** Contact development team for urgent issues

---

## 📋 Version Info

- **Application Version:** 1.0.0
- **Flask Version:** 2.x
- **Next.js Version:** 14.2.33
- **Python Version:** 3.8+
- **Node Version:** 16+
- **Last Updated:** 2024

---

## 📝 License

This project is proprietary and maintained by the CSR Development Team.

**© 2024 CSR Application Development Team. All rights reserved.**

---

## ✅ Quick Checklist

Before deploying or going into production:

- [ ] All tests passing: `python tests/test_all_cruds.py`
- [ ] Database schema verified: `python utilities/check_db_schema.py`
- [ ] Environment variables configured in `.env`
- [ ] Both services running without errors
- [ ] Admin login working with correct credentials
- [ ] User CRUD operations functioning
- [ ] CASCADE DELETE constraints verified
- [ ] API endpoints responding correctly
- [ ] Frontend connecting to backend successfully
- [ ] Error handling tested for edge cases

---

## 🎓 Learning Path

If you're new to this project, follow this learning path:

1. **Start Here:** Read this README (Quick Start → Installation)
2. **Run Tests:** `python tests/test_all_cruds.py` 
3. **Start Services:** `run.bat` or `npm run dev` + `python app.py`
4. **Explore Admin UI:** Visit http://localhost:3000
5. **Study Architecture:** Read `BCE_ARCHITECTURE_GUIDE.md`
6. **Check Flows:** Review diagrams in `BCE_ARCHITECTURE_DIAGRAMS.md`
7. **Debug Deeply:** Use login flow guide for authentication understanding
8. **Start Coding:** Implement new features following the patterns

---

**Happy coding! 🚀**