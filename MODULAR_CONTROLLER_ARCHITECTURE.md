# CSR App - Modular Controller Architecture

## Project Structure

```
src/controller/
├── auth/
│   ├── login_controller.py          # Login logic
│   ├── logout_controller.py         # Logout logic
│   ├── auth_middleware.py           # JWT auth middleware
│   └── __init__.py
├── userAccount/
│   ├── create_user_account_controller.py    # User creation
│   ├── view_user_account_controller.py      # User retrieval
│   ├── update_user_account_controller.py    # User updates
│   ├── suspend_user_account_controller.py   # User suspend/activate/delete
│   ├── search_user_account_controller.py    # User search
│   └── __init__.py
├── userProfile/
│   ├── create_user_profile_controller.py    # Role creation
│   ├── view_user_profile_controller.py      # Role retrieval
│   ├── update_user_profile_controller.py    # Role updates
│   ├── suspend_user_profile_controller.py   # Role deletion (CASCADE DELETE)
│   ├── search_user_profile_controller.py    # Role search
│   └── __init__.py
└── __init__.py
```

---

## API Endpoints

### **Authentication Endpoints**

| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| POST | `/api/auth/login` | `login_controller` | User login with credentials |
| POST | `/api/auth/logout` | `logout_controller` | User logout and token invalidation |

---

### **User Account Endpoints** (Requires USER_ADMIN role)

#### Create
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| POST | `/api/userAccount` | `create_user_account_controller` | Create new user account |

#### View
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| GET | `/api/userAccount` | `view_user_account_controller` | Get all users |
| GET | `/api/userAccount/<user_id>` | `view_user_account_controller` | Get specific user |

#### Update
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| PUT | `/api/userAccount/<user_id>` | `update_user_account_controller` | Update user details |

#### Suspend/Activate/Delete
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| PUT | `/api/userAccount/<user_id>/suspend` | `suspend_user_account_controller` | Suspend user (deactivate) |
| PUT | `/api/userAccount/<user_id>/activate` | `suspend_user_account_controller` | Activate user |
| DELETE | `/api/userAccount/<user_id>/delete` | `suspend_user_account_controller` | Delete user |

#### Search
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| POST | `/api/userAccount/search` | `search_user_account_controller` | Search users by criteria |

---

### **User Profile Endpoints** (Requires USER_ADMIN role)

#### Create
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| POST | `/api/userProfile` | `create_user_profile_controller` | Create new user profile (role) |

#### View
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| GET | `/api/userProfile` | `view_user_profile_controller` | Get all user profiles |
| GET | `/api/userProfile/<profile_id>` | `view_user_profile_controller` | Get specific user profile |

#### Update
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| PUT | `/api/userProfile/<profile_id>` | `update_user_profile_controller` | Update user profile details |

#### Delete (CASCADE DELETE)
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| DELETE | `/api/userProfile/<profile_id>/delete` | `suspend_user_profile_controller` | Delete user profile (cascades to users) |

#### Search
| Method | Endpoint | Controller | Description |
|--------|----------|-----------|-------------|
| POST | `/api/userProfile/search` | `search_user_profile_controller` | Search user profiles by name/code |

---

## Request/Response Examples

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin1",
  "password": "password123",
  "role_name": "User Admin"
}

Response (200):
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGc...",
    "user": {
      "id": 1,
      "username": "admin1",
      "full_name": "Admin One",
      "email": "admin1@test.com",
      "role": {
        "name": "User Admin",
        "code": "USER_ADMIN",
        "dashboard_route": "/admin"
      }
    }
  }
}
```

### Create User Account
```bash
POST /api/userAccount
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepass123",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role_id": 1
}

Response (201):
{
  "success": true,
  "message": "User account created successfully",
  "data": {
    "id": 100,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role_id": 1,
    "is_active": true,
    "created_at": "2025-10-25T10:30:00Z"
  }
}
```

### Create User Profile (Role)
```bash
POST /api/userProfile
Authorization: Bearer {token}
Content-Type: application/json

{
  "role_name": "Operations Manager",
  "role_code": "OP_MGR",
  "description": "Manages daily operations",
  "dashboard_route": "/operations"
}

Response (201):
{
  "success": true,
  "message": "User profile created successfully",
  "data": {
    "id": 5,
    "role_name": "Operations Manager",
    "role_code": "OP_MGR",
    "description": "Manages daily operations",
    "dashboard_route": "/operations",
    "created_at": "2025-10-25T10:30:00Z"
  }
}
```

---

## Code Organization Benefits

✅ **Single Responsibility**: Each controller handles ONE specific operation
✅ **Easy to Maintain**: Find and update logic in dedicated files
✅ **Scalable**: Add new operations by creating new controllers
✅ **Testable**: Easy to write unit tests for individual controllers
✅ **Reusable**: Controllers can be imported and composed
✅ **Clear API Structure**: URL patterns match logical grouping

---

## Frontend Integration

Update your `src/app/admin/page.js` to use the new endpoints:

```javascript
// User Account API calls
await fetch('/api/userAccount', { method: 'POST', ... })
await fetch('/api/userAccount', { method: 'GET', ... })
await fetch('/api/userAccount/1', { method: 'PUT', ... })
await fetch('/api/userAccount/1/suspend', { method: 'PUT', ... })
await fetch('/api/userAccount/1/activate', { method: 'PUT', ... })
await fetch('/api/userAccount/search', { method: 'POST', ... })

// User Profile API calls
await fetch('/api/userProfile', { method: 'POST', ... })
await fetch('/api/userProfile', { method: 'GET', ... })
await fetch('/api/userProfile/1', { method: 'PUT', ... })
await fetch('/api/userProfile/1/delete', { method: 'DELETE', ... })
await fetch('/api/userProfile/search', { method: 'POST', ... })
```

---

## Next Steps

1. ✅ Test all endpoints with the test scripts
2. Update frontend to use new endpoint URLs
3. Update CSS routes if needed
4. Add additional business logic as required
