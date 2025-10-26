# JWT Token Location Map - CSR Application

## 🎯 Quick Answer: Where Are JWT Tokens?

```
GENERATED: CONTROL LAYER (src/entity/user.py)
RETURNED:  BOUNDARY LAYER (src/controller/auth/login_controller.py)
STORED:    FRONTEND (localStorage in Next.js)
USED:      FRONTEND (sent with every request)
VERIFIED:  BOUNDARY LAYER (auth_middleware.py)
```

---

## 📍 Detailed Token Journey

### STAGE 1: Token Generation → **CONTROL LAYER**
**File:** `src/entity/user.py` (Lines 132-139)
**Layer:** CONTROL (Business Logic)

```python
# Inside User.authenticate() method
token_payload = {
    'user_id': user['id'],
    'username': user['username'],
    'email': user['email'],
    'role_id': user['role_id'],
    'iat': datetime.utcnow(),
    'exp': datetime.utcnow() + timedelta(hours=24)  ← Expires in 24 hours
}

token = jwt.encode(
    token_payload,
    SUPABASE_KEY,
    algorithm='HS256'
)
# Token created here: eyJhbGciOiJIUzI1NiIs...
```

**What happens:**
- ✅ JWT token is CREATED in CONTROL layer
- ✅ Contains user info + expiration time
- ✅ Signed with SUPABASE_KEY (secret key)
- ✅ Returns to BOUNDARY layer as part of result object

---

### STAGE 2: Token Returns to BOUNDARY → **BOUNDARY LAYER**
**File:** `src/controller/auth/login_controller.py` (Lines 35-55)
**Layer:** BOUNDARY (HTTP Interface)

```python
# In LoginController.login() method

# Step 1: Call CONTROL layer
result = User.authenticate(username, password, role_name)  ← Line 35

# Step 2: BOUNDARY receives result dict containing token from CONTROL
if result:  ← Line 38
    user_data = result
    
    # Step 3: BOUNDARY formats HTTP response
    return jsonify({  ← Line 41
        'success': True,
        'data': {
            'token': user_data.get('token'),  ← Token from CONTROL layer
            'user': {
                'id': user_data.get('id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'role_id': user_data.get('role_id')
            }
        },
        'message': 'Login successful'
    }), 200  ← HTTP response sent
```

**What happens:**
- ✅ BOUNDARY receives token from CONTROL
- ✅ Token is placed in JSON response body
- ✅ HTTP 200 response sent to frontend
- ✅ Token travels through HTTP to client

---

### STAGE 3: Token Stored in FRONTEND → **FRONTEND (localStorage)**
**File:** `src/app/page.js` (or any dashboard page)
**Layer:** FRONTEND (React/Next.js)

```javascript
// After login succeeds

// Frontend receives HTTP response with token
if (response.data.success) {
    
    // Step 1: Extract token from response
    const token = response.data.data.token;
    
    // Step 2: STORE token in localStorage
    localStorage.setItem('token', token);
    // Now stored as: localStorage.token = "eyJhbGciOiJIUzI1NiIs..."
    
    // Step 3: Store user data
    localStorage.setItem('user', JSON.stringify(response.data.data.user));
    
    // Step 4: Redirect to dashboard
    router.push('/admin');
}
```

**What happens:**
- ✅ Token extracted from HTTP response
- ✅ Stored in browser localStorage (persistent)
- ✅ Token remains here until user logs out or token expires
- ✅ Can be accessed by JavaScript: `localStorage.getItem('token')`

---

### STAGE 4: Token Used in Requests → **FRONTEND (sending)**
**File:** `src/app/admin/page.js` (or any component)
**Layer:** FRONTEND (React/Next.js)

```javascript
// When frontend needs to make authenticated API call

axios.get('http://localhost:5000/api/userAccount', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
        // Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    }
})
```

**What happens:**
- ✅ Frontend retrieves token from localStorage
- ✅ Adds it to HTTP Authorization header
- ✅ Sends with every protected API request
- ✅ Backend receives token in header

---

### STAGE 5: Token Verified → **BOUNDARY LAYER (Middleware)**
**File:** `src/controller/auth/auth_middleware.py`
**Layer:** BOUNDARY (HTTP Interface/Middleware)

```python
# Middleware that runs on every protected request

def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            
            # Step 1: Extract token from Authorization header
            auth_header = request.headers.get('Authorization')
            # auth_header = "Bearer eyJhbGciOiJIUzI1NiIs..."
            
            if not auth_header:
                return jsonify({'success': False, 'message': 'No token provided'}), 401
            
            # Step 2: Remove "Bearer " prefix
            token = auth_header.split(' ')[1]
            # token = "eyJhbGciOiJIUzI1NiIs..."
            
            # Step 3: Verify token signature
            try:
                payload = jwt.decode(
                    token,
                    SUPABASE_KEY,  ← Same secret key used to create token
                    algorithms=['HS256']
                )
                # If verification succeeds, payload contains: 
                # {user_id, username, email, role_id, iat, exp}
                
            except jwt.ExpiredSignatureError:
                return jsonify({'success': False, 'message': 'Token expired'}), 401
            
            except jwt.InvalidTokenError:
                return jsonify({'success': False, 'message': 'Invalid token'}), 401
            
            # Step 4: Check role
            if payload['role_id'] != required_role:
                return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
            
            # Step 5: Token valid - allow request to proceed
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
```

**What happens:**
- ✅ Token extracted from HTTP Authorization header
- ✅ Token signature verified using SUPABASE_KEY
- ✅ Token expiration checked
- ✅ Token role checked against required role
- ✅ If all valid → request proceeds
- ✅ If any check fails → 401/403 response

---

## 🔄 Complete Token Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TOKEN LIFECYCLE                                  │
└─────────────────────────────────────────────────────────────────────┘

1. USER LOGS IN
   ├─ Frontend sends: POST /api/auth/login
   │                  {username, password}
   └─ (No token yet)

2. BOUNDARY VALIDATES
   ├─ LoginController receives request
   └─ Extracts username & password

3. BOUNDARY CALLS CONTROL
   ├─ User.authenticate(username, password, role_name)
   └─ (Token generation happens here)

4. CONTROL GENERATES TOKEN ⭐
   ├─ Create JWT payload
   ├─ Sign with SUPABASE_KEY
   ├─ Generate token string: eyJhbGciOiJIUzI1NiIs...
   └─ Return to BOUNDARY in result dict

5. BOUNDARY RECEIVES TOKEN
   ├─ Extract token from result
   ├─ Include in JSON response
   └─ Send HTTP 200 OK to frontend

6. FRONTEND RECEIVES TOKEN
   ├─ Extract from response.data.data.token
   ├─ Store in localStorage.token
   └─ Now token is persistent

7. USER MAKES REQUESTS
   ├─ Frontend: axios.get(..., {headers: {Authorization: Bearer TOKEN}})
   └─ Token travels in HTTP header

8. BOUNDARY RECEIVES TOKEN
   ├─ Extract from Authorization header
   ├─ Middleware verifies signature
   ├─ Check expiration time
   ├─ Check role
   └─ If valid → allow request

9. REQUEST PROCEEDS
   ├─ BOUNDARY processes request
   ├─ CONTROL executes business logic
   ├─ ENTITY queries database
   └─ Response returned

10. TOKEN EXPIRES (24 hours later)
    ├─ exp_timestamp < current_time
    ├─ Next request with this token
    └─ Middleware returns 401 Token Expired
    └─ Frontend clears localStorage
    └─ User must re-login

```

---

## 📊 Token Location by Layer

```
┌───────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                           │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  localStorage.token = "eyJhbGciOiJIUzI1NiIs..."                       │
│                                                                       │
│  ✅ Token STORED here (persistent across page reloads)               │
│  ✅ Token SENT with each request (Authorization header)              │
│  ✅ Token RETRIEVED when making API calls                            │
│                                                                       │
│  axios.get('/api/userAccount', {                                     │
│    headers: {Authorization: `Bearer ${localStorage.token}`}          │
│  })                                                                   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
              ↑ HTTP Request (with token in header) ↓
┌───────────────────────────────────────────────────────────────────────┐
│                    BOUNDARY (Flask Controllers)                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  auth_middleware.py:                                                  │
│  ✅ Token EXTRACTED from request headers                             │
│  ✅ Token VERIFIED (signature check)                                 │
│  ✅ Token VALIDATED (expiration check)                               │
│                                                                       │
│  @require_role(Role.USER_ADMIN)  ← Middleware checks token          │
│  def get_all_users():                                                │
│      # Token already verified by middleware                           │
│      # Request allowed to proceed                                    │
│      ...                                                              │
│                                                                       │
│  login_controller.py:                                                 │
│  ✅ Token RECEIVED from CONTROL layer (in result dict)              │
│  ✅ Token FORMATTED into JSON response                               │
│  ✅ Token SENT back to frontend (HTTP 200)                           │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
              ↑ CONTROL layer creates token ↓
┌───────────────────────────────────────────────────────────────────────┐
│                  CONTROL (Entity Classes)                             │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  user.py - User.authenticate() method:                               │
│                                                                       │
│  token_payload = {                                                    │
│      'user_id': user['id'],                                          │
│      'username': user['username'],                                   │
│      'exp': datetime.utcnow() + timedelta(hours=24)                 │
│  }                                                                    │
│                                                                       │
│  token = jwt.encode(                                                  │
│      token_payload,                                                   │
│      SUPABASE_KEY,                                                    │
│      algorithm='HS256'                                               │
│  )  ← Token GENERATED here ⭐                                         │
│                                                                       │
│  return {                                                             │
│      'token': token,  ← Returned to BOUNDARY                         │
│      'user': {...}                                                    │
│  }                                                                    │
│                                                                       │
│  ✅ Token CREATED in CONTROL layer                                   │
│  ✅ Token RETURNED to BOUNDARY layer                                 │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
              ↓ Database query (no token here) ↓
┌───────────────────────────────────────────────────────────────────────┐
│                     ENTITY (Database)                                 │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  supabase_config.py / Database:                                      │
│                                                                       │
│  ✅ NO tokens stored in database                                     │
│  ✅ Only stores: users table with hashed passwords                   │
│  ✅ No token blacklist or token storage                              │
│                                                                       │
│  users table columns:                                                 │
│  - id, username, password (hashed), email, role_id, is_active       │
│  - NO token column                                                    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Points About JWT Token Location

### ✅ Token is CREATED in CONTROL Layer
**Why:** CONTROL layer contains business logic
- User authentication verification
- Role validation
- Token payload assembly
- JWT signing with secret key

**File:** `src/entity/user.py` Lines 132-139

### ✅ Token is RETURNED by BOUNDARY Layer
**Why:** BOUNDARY layer handles HTTP
- Receives token from CONTROL
- Formats into JSON response
- Sends HTTP 200 response to client

**File:** `src/controller/auth/login_controller.py` Lines 41-55

### ✅ Token is STORED in FRONTEND
**Why:** Frontend needs persistent storage
- localStorage survives page reloads
- Token persists across sessions
- Can be accessed by any component

**File:** `src/app/*.js` (any page, e.g., `admin/page.js` Lines 68-69)

### ✅ Token is USED by FRONTEND
**Why:** Frontend makes all API requests
- Every request includes token in header
- Frontend retrieves from localStorage
- Sends as: `Authorization: Bearer <TOKEN>`

**File:** `src/app/*.js` (any component making API calls)

### ✅ Token is VERIFIED by BOUNDARY Layer
**Why:** BOUNDARY layer protects endpoints
- Middleware extracts token from header
- Verifies signature with secret key
- Checks expiration time
- Validates role

**File:** `src/controller/auth/auth_middleware.py`

### ❌ Token is NOT stored in ENTITY Layer
**Why:** Stateless JWT design
- No token table in database
- No token blacklist
- No server-side token storage
- ENTITY only handles business data

---

## 📋 Token Locations Summary Table

| Location | Storage | Used For | File |
|----------|---------|----------|------|
| **CONTROL** | ✅ Temporary (during execution) | Token generation | `src/entity/user.py` |
| **BOUNDARY** | ✅ Temporary (during response) | Token formatting | `src/controller/auth/login_controller.py` |
| **BOUNDARY** | ✅ Temporary (request processing) | Token verification | `src/controller/auth/auth_middleware.py` |
| **FRONTEND** | ✅ Persistent (localStorage) | Token storage & sending | `src/app/*.js` |
| **ENTITY** | ❌ Never stored | N/A (not needed) | Database |

---

## 🎓 Answer to Your Question

**WHERE ARE JWT TOKENS AT?**

- **Generated:** CONTROL Layer (`src/entity/user.py`)
- **Returned:** BOUNDARY Layer (HTTP response, `src/controller/auth/login_controller.py`)
- **Stored:** FRONTEND Layer (localStorage, `src/app/page.js` and dashboards)
- **Sent:** FRONTEND Layer (every request header)
- **Verified:** BOUNDARY Layer (middleware, `src/controller/auth/auth_middleware.py`)
- **Persisted:** FRONTEND Layer (localStorage, NOT database)

**NOT in ENTITY Layer** → Because JWT is stateless; no database storage needed.

---

**Summary:**
```
Token Flow: CONTROL (Create) → BOUNDARY (Return) → FRONTEND (Store) → FRONTEND (Send) → BOUNDARY (Verify) → ✅ Request Allowed
```

