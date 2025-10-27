# Quick Start Guide - CSR Application

**Last Updated:** October 27, 2025
**Latest Enhancements:** Input validation, sanitization, and business logic improvements

## 🚀 Start the Application in 3 Steps

### Step 1: Open Command Prompt or PowerShell
Navigate to the `csr_app` folder

### Step 2: Run One of These Commands

**Option A - Windows Command Prompt (CMD):**
```bash
run.bat
```

**Option B - Windows PowerShell:**
```powershell
.\run.ps1
```

**Option C - Manual Start:**
```bash
# Terminal 1
python app.py

# Terminal 2 (new terminal window)
npm run dev
```

### Step 3: Open Browser
Go to: `http://localhost:3000`

---

## 📋 Test Login Credentials

### User Admin
- **Username:** admin
- **Password:** (as set in Supabase)
- **Role:** User Admin

---

## 🎯 What You Can Do

Once logged in as User Admin, you have access to:

✅ **View All Users** - See list of all registered users
✅ **Create Users** - Add new users to the system
✅ **Search Users** - Find users by name, email, or username
✅ **Update Users** - Edit user information
✅ **Suspend Users** - Deactivate user accounts
✅ **Activate Users** - Reactivate suspended accounts

---

## 🌐 Important URLs

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:5000
- **API Health:** http://localhost:5000/api/health

---

## 📝 Default Test Users

Create test users from the dashboard for testing different roles:
- User Admin
- PIN
- CSR Rep
- Platform Management

---

## 🔐 Input Validation & Security

All user input is automatically validated and sanitized:

**Username Requirements:**
- 3-20 characters
- Alphanumeric + hyphens/underscores

**Password Requirements:**
- Minimum 8 characters
- Must have uppercase letter (A-Z)
- Must have lowercase letter (a-z)
- Must have digit (0-9)
- Example: `SecurePass123` ✅

**Email Requirements:**
- Valid email format
- Must be unique (no duplicates)
- Example: `user@example.com` ✅

**Full Name Requirements:**
- 2-100 characters
- Must contain letters

If validation fails, you'll get a clear error message telling you what's wrong!

---

## 📞 Troubleshooting

### Port Already in Use
If you get "Port 5000 in use" or "Port 3000 in use":
- Close other applications using these ports
- Or change ports in `.env` file

### Python Not Found
- Install Python from https://www.python.org/
- Make sure to check "Add to PATH" during installation

### Node Not Found
- Install Node.js from https://nodejs.org/
- Make sure to check "Add to PATH" during installation

### Virtual Environment Error
- Delete the `venv` folder
- Run `run.bat` or `run.ps1` again

---

## 📚 For More Details

See:
- `README.md` - Full documentation
- `VALIDATION_SUMMARY.md` - Complete validation reference
- `QUICK_REFERENCE.md` - API quick reference
- `ADMIN_DASHBOARD_GUIDE.md` - Dashboard features
- `HOW_JSON_AND_WEB_WORKS.md` - Understanding JSON & web requests

---

## ⚠️ Important

- Never commit `.env` file to git
- Keep your Supabase credentials secret
- Change JWT secret keys in production

---

**Happy Coding! 🎉**