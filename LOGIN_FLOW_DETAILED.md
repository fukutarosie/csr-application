"""
COMPLETE LOGIN FLOW WALKTHROUGH
Demonstrating BCE Architecture with Exact File Locations and Line Numbers
"""

# ==============================================================================
# STEP 1: FRONTEND (Next.js) - React Component
# ==============================================================================

File: src/app/admin/page.js (or any page that needs to login)
Lines: 1-50 (Login logic in the application)

EXAMPLE CODE:
```javascript
// File: src/app/admin/page.js
// This is where users login to access the admin dashboard

import axios from 'axios';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  
  // User enters credentials and clicks "Login"
  const handleLogin = async (e) => {
    e.preventDefault();
    
    // ↓ STEP 1: FRONTEND sends HTTP request to BOUNDARY layer
    try {
      const response = await axios.post(
        'http://localhost:5000/api/auth/login',  ← BOUNDARY endpoint
        {
          username: username,        ← User input from form
          password: password,        ← User input from form
          role_name: 'User Admin'
        }
      );
      
      // STEP 4: Frontend receives response from BOUNDARY
      if (response.data.success) {
        // Save JWT token to localStorage
        localStorage.setItem('token', response.data.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.data.user));
        
        // Redirect to admin dashboard
        router.push('/admin');
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError('Login failed: ' + err.message);
    }
  };
  
  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
      {error && <p style={{color: 'red'}}>{error}</p>}
    </form>
  );
}
```

FRONTEND FLOW:
User enters username/password
         ↓
Clicks "Login" button
         ↓
handleLogin() triggered
         ↓
axios.post('http://localhost:5000/api/auth/login', {username, password})
         ↓
HTTP POST Request sent to Flask Backend
         ↓
[NOW we enter the BOUNDARY layer]

---

# ==============================================================================
# STEP 2: BOUNDARY LAYER (HTTP Interface) - Flask Controller
# ==============================================================================

File: src/controller/auth/login_controller.py
Lines: 1-70 (Complete controller)

EXACT CODE:
```python
# File: src/controller/auth/login_controller.py
# Lines: 1-70
# This is the BOUNDARY layer - it handles HTTP requests

"""Login Controller - Handles user authentication via HTTP"""

from flask import Blueprint, request, jsonify
from src.entity import User
from src.controller.auth.auth_middleware import require_role, Role

login_blueprint = Blueprint('login', __name__, url_prefix='/api/auth')

class LoginController:
    @login_blueprint.route('/login', methods=['POST'])  ← Line 12
    def login():
        """
        BOUNDARY LAYER: HTTP Endpoint
        
        This function receives HTTP requests from Next.js frontend
        """
        try:
            # ====== BOUNDARY: Extract HTTP request data ======
            data = request.json  ← Line 20: Get JSON from request
            
            username = data.get('username')     ← Line 22: Extract username
            password = data.get('password')     ← Line 23: Extract password
            role_name = data.get('role_name')   ← Line 24: Extract role_name
            
            # ====== BOUNDARY: Input Validation ======
            if not username or not password:  ← Line 27
                return jsonify({
                    'success': False,
                    'message': 'Username and password are required'
                }), 400  ← Return 400 Bad Request if missing
            
            # ====== CALL CONTROL LAYER ======
            # Now we call the entity User class (which contains business logic)
            result = User.authenticate(username, password, role_name)  ← Line 35
            
            # The User.authenticate() method is in the CONTROL layer
            # It handles all business logic (password verification, etc.)
            
            if result:  ← Line 38: Check if authentication succeeded
                user_data = result  ← CONTROL layer returned user object
                
                # ====== BOUNDARY: Format HTTP Response ======
                return jsonify({  ← Line 41: Create JSON response
                    'success': True,
                    'data': {
                        'token': user_data.get('token'),
                        'user': {
                            'id': user_data.get('id'),
                            'username': user_data.get('username'),
                            'email': user_data.get('email'),
                            'role_id': user_data.get('role_id')
                        }
                    },
                    'message': 'Login successful'
                }), 200  ← Return 200 OK status
            else:
                # ====== BOUNDARY: Format Error Response ======
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401  ← Return 401 Unauthorized if auth failed
        
        except Exception as e:
            # ====== BOUNDARY: Catch all exceptions ======
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500  ← Return 500 Server Error for unexpected errors

# Flask registers this blueprint in app.py so the route /api/auth/login works
```

BOUNDARY LAYER BREAKDOWN:

@login_blueprint.route('/login', methods=['POST'])
    ↓ This creates HTTP endpoint: POST /api/auth/login
    
Line 20: data = request.json
    ↓ Extracts the JSON body from HTTP request
    ↓ Example: {"username": "admin1", "password": "password123"}
    
Line 22-24: Extract individual fields
    ↓ Get username, password, role_name
    
Line 27: if not username or not password:
    ↓ BOUNDARY validates input (did user send required fields?)
    ↓ If missing → return 400 Bad Request immediately
    
Line 35: result = User.authenticate(username, password, role_name)
    ↓ **CALL CONTROL LAYER**
    ↓ Pass data to User class in entity layer
    ↓ User class handles all business logic (password verification, JWT generation)
    
Line 41-55: return jsonify({...}), 200/401/500
    ↓ **BOUNDARY formats response**
    ↓ Converts Python dict to JSON
    ↓ Sends HTTP status code back to client

HTTP REQUEST/RESPONSE:
┌─ Frontend sends ────────────────────┐
│ POST /api/auth/login                │
│ Content-Type: application/json      │
│                                      │
│ {                                    │
│   "username": "admin1",              │
│   "password": "password123",         │
│   "role_name": "User Admin"          │
│ }                                    │
└──────────────────────────────────────┘
         ↓↓↓ BOUNDARY processes ↓↓↓
┌─ Backend returns ──────────────────┐
│ 200 OK                              │
│ Content-Type: application/json      │
│                                      │
│ {                                    │
│   "success": true,                   │
│   "data": {                          │
│     "token": "eyJhbGciOiJIUzI1...", │
│     "user": {                        │
│       "id": 1,                       │
│       "username": "admin1",          │
│       "email": "admin@...",          │
│       "role_id": 1                   │
│     }                                │
│   },                                 │
│   "message": "Login successful"      │
│ }                                    │
└──────────────────────────────────────┘

---

# ==============================================================================
# STEP 3: CONTROL LAYER (Business Logic) - Entity Class
# ==============================================================================

File: src/entity/user.py
Lines: 1-100+ (User class with authenticate method)

EXACT CODE:
```python
# File: src/entity/user.py
# Lines: ~90-150 (authenticate method)
# This is the CONTROL layer - it handles business logic

from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from werkzeug.security import check_password_hash
from .supabase_config import get_supabase, SUPABASE_KEY

class User:
    
    @staticmethod
    def authenticate(username: str, password: str, role_name: str = None) -> Optional[Dict]:  ← Line 95
        """
        CONTROL LAYER: Business Logic
        
        This method receives data from BOUNDARY layer
        and applies business rules before querying database
        """
        
        # ====== CONTROL: Get user from database ======
        supabase = get_supabase()  ← Line 106: Get database connection
        
        # ====== CONTROL RULE 1: User must exist ======
        user_response = supabase.table('users').select('*').eq('username', username).execute()  ← Line 110
        
        # This queries the database (ENTITY layer responsibility)
        # SELECT * FROM users WHERE username = 'admin1'
        
        if not user_response.data:  ← Line 112: Check if user found
            return None  ← User not found, authentication fails
        
        user = user_response.data[0]  ← Line 115: Get the user record
        
        # ====== CONTROL RULE 2: User must be active ======
        if not user['is_active']:  ← Line 118: Check if account is suspended
            raise ValueError("User account is suspended")  ← Reject suspended users
        
        # ====== CONTROL RULE 3: Password must be correct ======
        if not check_password_hash(user['password'], password):  ← Line 121
            return None  ← Wrong password, authentication fails
        
        # The password in database is HASHED like: $2b$12$abc123...
        # check_password_hash() compares the hashed password with plain text
        # Returns True only if hash matches the password
        
        # ====== CONTROL RULE 4: Role must be valid (if specified) ======
        if role_name:  ← Line 125
            user_role = user.get('role_id')
            role = Role.get_role_by_id(user_role)  ← Line 127
            
            if not role or role.get('role_name') != role_name:  ← Line 128
                raise ValueError("User does not have required role")
        
        # ====== CONTROL: All business rules passed ======
        # Now generate JWT token (security/authentication logic)
        
        token_payload = {  ← Line 132: Create token data
            'user_id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role_id': user['role_id'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)  ← Token valid for 24 hours
        }
        
        token = jwt.encode(  ← Line 139: Generate JWT token
            token_payload,
            SUPABASE_KEY,
            algorithm='HS256'
        )
        
        # Return the authenticated user with token
        return {  ← Line 143: Return user object with token
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role_id': user['role_id'],
            'is_active': user['is_active'],
            'token': token  ← JWT token for future authenticated requests
        }
```

CONTROL LAYER BREAKDOWN:

Line 110: supabase.table('users').select('*').eq('username', username).execute()
    ↓ **CALL ENTITY LAYER** (database query)
    ↓ Executes: SELECT * FROM users WHERE username = 'admin1'
    ↓ Returns database record
    
Line 112: if not user_response.data:
    ↓ **CONTROL RULE 1**: User must exist
    ↓ If user not found → return None (failed authentication)
    
Line 118: if not user['is_active']:
    ↓ **CONTROL RULE 2**: User account must be active
    ↓ If suspended → raise ValueError
    ↓ This prevents suspended users from logging in
    
Line 121: if not check_password_hash(user['password'], password):
    ↓ **CONTROL RULE 3**: Password must be correct
    ↓ check_password_hash is a security function that:
    ↓   1. Takes the HASHED password from database: $2b$12$abc123...
    ↓   2. Takes the plain text password user entered: 'password123'
    ↓   3. Hashes the plain text and compares with stored hash
    ↓   4. Returns True only if they match
    ↓ If wrong password → return None (failed authentication)
    
Line 128: if not role or role.get('role_name') != role_name:
    ↓ **CONTROL RULE 4**: User must have the requested role
    ↓ If role mismatch → raise ValueError
    
Line 132-139: token_payload and jwt.encode()
    ↓ **CONTROL**: Generate JWT token for authenticated session
    ↓ JWT contains user info and expires in 24 hours
    ↓ This token is returned to frontend
    ↓ Frontend stores it in localStorage
    ↓ Frontend sends it with every future request

BUSINESS LOGIC FLOW:

User.authenticate('admin1', 'password123', 'User Admin')
    ↓
    ├─ RULE 1: User exists? → Query DB (ENTITY)
    │                      ↓ Not found → return None
    │
    ├─ RULE 2: User active? → Check is_active field
    │                      ↓ Suspended → raise Error
    │
    ├─ RULE 3: Password correct? → check_password_hash()
    │                            ↓ Wrong → return None
    │
    ├─ RULE 4: Role valid? → Query DB for role (ENTITY)
    │                     ↓ Invalid → raise Error
    │
    └─ All rules passed → Generate JWT token → Return user object

---

# ==============================================================================
# STEP 4: ENTITY LAYER (Data Persistence) - Database Queries
# ==============================================================================

File: src/entity/user.py (same file, but different methods)
Lines: 40-50, 60-70 (Database helper methods)

EXACT CODE:
```python
# File: src/entity/user.py
# Lines: ~40-50
# These are ENTITY layer methods - direct database access

class User:
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:  ← Line 45
        """
        ENTITY LAYER: Direct Database Access
        
        Pure database query with no business logic
        """
        supabase = get_supabase()  ← Line 52: Get database connection
        
        # ENTITY: Execute raw database query
        response = supabase.table('users').select('*').eq('username', username).execute()  ← Line 55
        
        # SQL: SELECT * FROM users WHERE username = 'admin1'
        
        return response.data[0] if response.data else None  ← Line 57: Return result
```

ENTITY LAYER BREAKDOWN:

Line 55: supabase.table('users').select('*').eq('username', username).execute()
    ↓ This is pure database access - NO business logic
    ↓ It:
    │   1. Connects to Supabase PostgreSQL
    │   2. Selects the 'users' table
    │   3. Gets ALL columns (*)
    │   4. Filters WHERE username = 'admin1'
    │   5. Executes the query
    ↓
    ↓ Database returns:
    │ {
    │   id: 1,
    │   username: 'admin1',
    │   email: 'admin@example.com',
    │   password: '$2b$12$abc123...xyz789',  ← HASHED password
    │   is_active: true,
    │   role_id: 1,
    │   created_at: '2024-01-15T10:30:00'
    │ }

Line 57: return response.data[0] if response.data else None
    ↓ Returns the first row if found
    ↓ Returns None if not found
    ↓ No transformation, no business logic

DATABASE TABLE STRUCTURE:

users table (in Supabase):
┌──────────────────────────────────────────────────────────┐
│ Column     │ Type    │ Example Value                     │
├──────────────────────────────────────────────────────────┤
│ id         │ int     │ 1                                 │
│ username   │ text    │ 'admin1'                          │
│ email      │ text    │ 'admin@example.com'               │
│ password   │ text    │ '$2b$12$N9qo8uCoU123...'         │ ← HASHED
│ full_name  │ text    │ 'Admin User'                      │
│ role_id    │ int     │ 1 (foreign key to roles table)   │
│ is_active  │ bool    │ true                              │
│ created_at │ timestamp│ '2024-01-15T10:30:00'            │
└──────────────────────────────────────────────────────────┘

Password Storage Note:
- Plain text entered: 'password123'
- Stored in DB (hashed): '$2b$12$N9qo8uCoU...'
- During login:
  1. User enters 'password123'
  2. CONTROL layer gets hashed version from DB
  3. check_password_hash('$2b$12$...', 'password123') → True
  4. Only then is login successful

---

# ==============================================================================
# COMPLETE LOGIN FLOW - ALL LAYERS TOGETHER
# ==============================================================================

FULL SEQUENCE WITH LINE NUMBERS:

1. FRONTEND (Next.js)
   src/app/page.js ~ Line 50-60
   └─ User enters username "admin1" and password "password123"
   └─ Clicks "Login" button
   └─ handleLogin() function triggered
   
2. FRONTEND → BOUNDARY
   src/app/page.js ~ Line 55
   └─ axios.post('http://localhost:5000/api/auth/login', {
        username: 'admin1',
        password: 'password123'
      })
   └─ HTTP POST REQUEST SENT
   
3. BOUNDARY LAYER
   src/controller/auth/login_controller.py ~ Line 16-60
   └─ Line 20: data = request.json  ← Receive request
   └─ Line 22-24: Extract username, password, role_name
   └─ Line 27: Validate inputs not empty
   └─ Line 35: result = User.authenticate('admin1', 'password123', 'User Admin')
                ↓ CALL CONTROL LAYER
   
4. CONTROL LAYER
   src/entity/user.py ~ Line 95-145
   └─ Line 106: supabase = get_supabase()  ← Connect to DB
   └─ Line 110: Query database for user (ENTITY call)
                ↓ SELECT * FROM users WHERE username = 'admin1'
   └─ Line 112: Check if user exists (RULE 1)
   └─ Line 118: Check if user is active (RULE 2)
   └─ Line 121: check_password_hash() (RULE 3)
                ├─ Hash: $2b$12$N9qo8uCoU...
                ├─ Plain: 'password123'
                └─ Compare → True = password correct
   └─ Line 128: Check if user has required role (RULE 4)
   └─ Line 132-139: Generate JWT token
   └─ Line 143: Return {id, username, email, role_id, token}
   
5. BOUNDARY LAYER (Response)
   src/controller/auth/login_controller.py ~ Line 41-55
   └─ Check if result is not None
   └─ Line 42: return jsonify({...}), 200
              └─ Convert Python dict to JSON
              └─ Add HTTP status 200 OK
   
6. HTTP RESPONSE SENT
   └─ 200 OK
   └─ Content-Type: application/json
   └─ Body: {
        "success": true,
        "data": {
          "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "user": {
            "id": 1,
            "username": "admin1",
            "email": "admin@example.com",
            "role_id": 1
          }
        },
        "message": "Login successful"
      }
   
7. FRONTEND (Next.js)
   src/app/page.js ~ Line 65-75
   └─ response.data.success = true
   └─ Line 68: localStorage.setItem('token', token)
              └─ Save JWT token
   └─ Line 69: localStorage.setItem('user', user_object)
              └─ Save user info
   └─ Line 71: router.push('/admin')
              └─ Redirect to admin dashboard

---

# ==============================================================================
# HOW NEXT.JS USES THE TOKEN FOR FUTURE REQUESTS
# ==============================================================================

After login, frontend has token in localStorage:
localStorage.token = "eyJhbGciOiJIUzI1NiIs..."

For any protected endpoint, frontend includes token:

```javascript
// Example: Get all users (requires authentication)
axios.get('http://localhost:5000/api/userAccount', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`  ← JWT token
  }
})
```

BOUNDARY receives request with token:

```python
# src/controller/userAccount/view_user_account_controller.py ~ Line 15
@view_user_account_blueprint.route('/', methods=['GET'])
@require_role(Role.USER_ADMIN)  ← Line 16: Middleware checks token
def get_all():
    # If token is invalid or missing → 401 Unauthorized
    # If token valid and user is USER_ADMIN → proceed
    # Otherwise → 403 Forbidden
```

---

# ==============================================================================
# FILE LOCATIONS QUICK REFERENCE
# ==============================================================================

FRONTEND:
- src/app/page.js (or any component)
  └─ Lines 50-75: Login form and axios request

BOUNDARY LAYER:
- src/controller/auth/login_controller.py
  └─ Lines 12-60: @login_blueprint.route('/login', methods=['POST'])
  └─ Line 20: data = request.json
  └─ Line 22-24: Extract fields
  └─ Line 35: User.authenticate() call

CONTROL LAYER:
- src/entity/user.py
  └─ Lines 95-145: User.authenticate() method
  └─ Line 110: Database query (ENTITY call)
  └─ Line 112-128: Business rules validation
  └─ Line 132-139: JWT token generation
  └─ Line 143: Return user with token

ENTITY LAYER:
- src/entity/user.py
  └─ Lines 45-57: User.get_user_by_username() method
  └─ Line 55: supabase.table('users').select('*')...
  └─ Line 57: Return database result

DATABASE:
- Supabase PostgreSQL (Cloud)
  └─ users table
  └─ Contains: id, username, password (hashed), email, role_id, is_active

---

# ==============================================================================
# KEY CONCEPTS TO REMEMBER
# ==============================================================================

1. SEPARATION OF CONCERNS
   ✓ Frontend only talks to /api/auth/login
   ✓ Frontend doesn't know about database
   ✓ BOUNDARY handles HTTP only
   ✓ CONTROL handles business logic only
   ✓ ENTITY handles database only

2. DATA FLOW IS UNIDIRECTIONAL
   Frontend → BOUNDARY → CONTROL → ENTITY → Database
   Database → ENTITY → CONTROL → BOUNDARY → Frontend

3. PASSWORD SECURITY
   ✓ Plain password entered by user
   ✓ BOUNDARY receives it in HTTP request
   ✓ CONTROL receives plain password
   ✓ ENTITY retrieves hashed password from DB
   ✓ CONTROL compares using check_password_hash()
   ✓ Hashed password NEVER sent back to frontend

4. JWT TOKEN
   ✓ Generated by CONTROL layer during authentication
   ✓ Sent to BOUNDARY
   ✓ BOUNDARY includes in JSON response
   ✓ Frontend stores in localStorage
   ✓ Frontend sends with every future request
   ✓ BOUNDARY validates token using @require_role middleware

5. ERROR HANDLING
   ✓ BOUNDARY validates format (400 Bad Request)
   ✓ CONTROL validates business rules (401 Unauthorized)
   ✓ ENTITY handles database errors (500 Server Error)
   ✓ BOUNDARY catches all exceptions and returns appropriate status

"""
