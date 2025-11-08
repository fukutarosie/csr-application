# CSR App - Login Credentials

## Services Running

- **Backend (Flask)**: http://localhost:5000
- **Frontend (Next.js)**: http://localhost:3001 (Note: Port 3001, not 3000)

## Login Password

All users have been reset to use the same password:

**Password**: `password123`

## Available Test Users

### User Admin (Role: User Admin)
- `admin1` / password123
- `admin2` / password123
- `admin3` / password123
- `admin4` / password123
- `admin5` / password123
- `admin6` / password123
- `admin10` / password123
- `admin15` / password123
- `admin19` / password123

### PIN Users (Role: PIN - Person In Need)
- `pin_user1` / password123
- `pin_user2` / password123
- `testuser_192220` / password123
- `directtest_8966` / password123

### CSR Representatives (Role: CSR Rep)
- `csr_rep1` / password123
- `csr_rep2` / password123
- `csr_rep3` / password123
- `csr_rep4` / password123
- `csr_rep6` / password123
- `csr_representative3` / password123

### Platform Management (Role: Platform Management)
- `platform_mgr1` / password123
- `platform_mgr2` / password123

## Login Instructions

1. Open your browser and go to: **http://localhost:3001**
2. Select a role from the dropdown
3. Enter any username from the list above
4. Enter password: `password123`
5. Click Login

## Important Notes

- The password requirement is **8 characters minimum**
- The old password `csr123` (6 characters) will NOT work
- All 36 users in the database now use `password123`
- Frontend is on port **3001** because port 3000 was already in use

## Stopping the Services

The backend and frontend are running in separate terminal windows:
- Press `Ctrl+C` in each terminal to stop the services

## Issue That Was Fixed

**Problem**: Login was failing with "Invalid password" error

**Cause**: Test users were created with password `csr123` (6 characters), but the password validator requires at least 8 characters

**Solution**: Reset all user passwords to `password123` (11 characters) using the `reset_all_passwords.py` script

## Testing Login via API

```powershell
$body = @{ 
    username = "admin1"
    password = "password123"
    role_name = "User Admin" 
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

Expected response: 200 OK with JWT token and user data






