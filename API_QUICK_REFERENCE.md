# Quick Start: New Modular Controller Endpoints

## 🎯 API Endpoint Quick Reference

### Authentication
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"password123","role_name":"User Admin"}'

# Logout (requires token)
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer {token}"
```

---

### User Account CRUD

#### Create User
```bash
curl -X POST http://localhost:5000/api/userAccount \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "username":"john_doe",
    "password":"securepass123",
    "email":"john@example.com",
    "full_name":"John Doe",
    "role_id":1
  }'
```

#### Get All Users
```bash
curl -X GET http://localhost:5000/api/userAccount \
  -H "Authorization: Bearer {token}"
```

#### Get Specific User
```bash
curl -X GET http://localhost:5000/api/userAccount/1 \
  -H "Authorization: Bearer {token}"
```

#### Update User
```bash
curl -X PUT http://localhost:5000/api/userAccount/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"newemail@example.com",
    "full_name":"John Updated",
    "role_id":2
  }'
```

#### Suspend User
```bash
curl -X PUT http://localhost:5000/api/userAccount/1/suspend \
  -H "Authorization: Bearer {token}"
```

#### Activate User
```bash
curl -X PUT http://localhost:5000/api/userAccount/1/activate \
  -H "Authorization: Bearer {token}"
```

#### Delete User
```bash
curl -X DELETE http://localhost:5000/api/userAccount/1/delete \
  -H "Authorization: Bearer {token}"
```

#### Search Users
```bash
curl -X POST http://localhost:5000/api/userAccount/search \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "username":"john",
    "email":"@example.com",
    "full_name":"John"
  }'
```

---

### User Profile (Role) CRUD

#### Create Profile
```bash
curl -X POST http://localhost:5000/api/userProfile \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name":"Manager",
    "role_code":"MGR",
    "description":"Manager role",
    "dashboard_route":"/manager"
  }'
```

#### Get All Profiles
```bash
curl -X GET http://localhost:5000/api/userProfile \
  -H "Authorization: Bearer {token}"
```

#### Get Specific Profile
```bash
curl -X GET http://localhost:5000/api/userProfile/1 \
  -H "Authorization: Bearer {token}"
```

#### Update Profile
```bash
curl -X PUT http://localhost:5000/api/userProfile/1 \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name":"Senior Manager",
    "role_code":"SR_MGR",
    "description":"Senior Manager role"
  }'
```

#### Delete Profile (CASCADE DELETE)
```bash
curl -X DELETE http://localhost:5000/api/userProfile/1/delete \
  -H "Authorization: Bearer {token}"
```

#### Search Profiles
```bash
curl -X POST http://localhost:5000/api/userProfile/search \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"search":"manager"}'
```

---

## 📝 Frontend Integration

### Update your JavaScript API calls:

```javascript
// Before (Old endpoints - DEPRECATED)
const response = await fetch('/api/users', {
  method: 'GET',
  headers: { 'Authorization': `Bearer ${token}` }
});

// After (New endpoints - USE THESE)
const response = await fetch('/api/userAccount', {
  method: 'GET',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Complete endpoint mapping:

| Feature | Old | New |
|---------|-----|-----|
| List Users | GET /api/users | GET /api/userAccount |
| Create User | POST /api/users/create | POST /api/userAccount |
| Get User | GET /api/users/<id> | GET /api/userAccount/<id> |
| Update User | PUT /api/users/<id> | PUT /api/userAccount/<id> |
| Delete User | DELETE /api/users/<id> | DELETE /api/userAccount/<id>/delete |
| Suspend User | PUT /api/users/<id>/suspend | PUT /api/userAccount/<id>/suspend |
| List Roles | GET /api/roles | GET /api/userProfile |
| Create Role | POST /api/roles | POST /api/userProfile |
| Delete Role | DELETE /api/roles/<id> | DELETE /api/userProfile/<id>/delete |

---

## 🧪 Testing Commands

### Test All CRUD Operations
```bash
python test_all_cruds.py
```

### Test CASCADE DELETE
```bash
python test_cascade_delete.py
```

---

## 📍 File Locations

All new controllers located in:
- `src/controller/auth/` - Authentication
- `src/controller/userAccount/` - User account operations
- `src/controller/userProfile/` - User profile/role operations

---

## 🎯 Common Response Format

All endpoints return:
```json
{
  "success": true/false,
  "message": "Operation successful",
  "data": { /* response data */ },
  "count": 5  // For list operations
}
```

---

## ⚠️ Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET, PUT) |
| 201 | Created (POST) |
| 400 | Bad request (missing fields) |
| 401 | Unauthorized (no token/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found (resource doesn't exist) |
| 500 | Server error |

---

## 🔐 Authentication

All endpoints except `/api/auth/login` require:
```bash
Authorization: Bearer {jwt_token}
```

Get token from login response.

---

## ✅ Checklist for Migration

- [ ] Update all fetch() calls in `src/app/admin/page.js`
- [ ] Test each endpoint with curl or Postman
- [ ] Run `python test_all_cruds.py`
- [ ] Run `python test_cascade_delete.py`
- [ ] Test in browser at http://localhost:3000/admin
- [ ] Commit changes: `git add . && git commit -m "update: API endpoints for modular controllers"`
- [ ] Push to GitHub: `git push origin main`

---

**Happy API testing!** 🚀
