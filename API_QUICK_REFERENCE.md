# Quick Start: New Modular Controller Endpoints

**Last Updated:** October 27, 2025
**Latest Enhancements:** Input validation, sanitization, error handling, and activity logging

## 🔒 Input Validation Rules

All endpoints validate input according to these rules:

### Field Validation Rules

| Field | Rules | Example |
|-------|-------|---------|
| username | 3-20 chars, alphanumeric + - and _ | `john_doe-123` ✅ |
| password | 8+ chars, uppercase, lowercase, digit | `SecurePass123` ✅ |
| email | Valid email format, max 100 chars, unique | `john@example.com` ✅ |
| full_name | 2-100 chars, must contain letters | `John Michael Doe` ✅ |
| phone | 10+ digits | `5551234567` ✅ |
| role_id | Positive integer | `1`, `2`, `3` ✅ |

### Error Responses

If validation fails, you'll receive:

```json
{
  "success": false,
  "message": "Specific error description",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

**Common Error Codes:**
- `INVALID_JSON` - Request is not valid JSON
- `EMPTY_BODY` - Request body is empty
- `MISSING_FIELDS` - Required fields not provided
- `VALIDATION_ERROR` - Field format invalid
- `DUPLICATE_EMAIL` - Email already exists
- `DUPLICATE_USERNAME` - Username already exists
- `INVALID_TOKEN` - JWT token invalid/expired
- `USER_NOT_FOUND` - User doesn't exist

---

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

- `src/controller/auth/` - Authentication
- `src/controller/userAccount/` - User account operations
- `src/controller/userProfile/` - User profile/role operations

---

## 📊 HTTP Status Codes

```
200 OK                 - Request succeeded
201 Created            - Resource created successfully
400 Bad Request        - Validation error or malformed request
401 Unauthorized       - Missing or invalid authentication
404 Not Found          - Resource doesn't exist
409 Conflict           - Duplicate resource (email/username exists)
500 Server Error       - Internal server error
```

---

## 🔐 Security Headers

All requests to protected endpoints require:

```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

**Getting a token:**
1. Login with valid credentials
2. Receive JWT token in response
3. Include token in `Authorization` header for subsequent requests
4. Token expires after configured duration
5. Use logout endpoint to invalidate token

---

## 📚 Related Documentation

- **[VALIDATION_SUMMARY.md](./VALIDATION_SUMMARY.md)** - Complete validation rules and error handling
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Helper functions and utilities
- **[HOW_JSON_AND_WEB_WORKS.md](./HOW_JSON_AND_WEB_WORKS.md)** - Understanding requests/responses
- **[CONTROLLER_IMPROVEMENTS_GUIDE.md](./CONTROLLER_IMPROVEMENTS_GUIDE.md)** - Implementation details

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
