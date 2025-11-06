# 📋 Scripts Inventory - What Each Script Does

## ✅ **ESSENTIAL SCRIPTS - KEEP THESE**

### 🚀 Main Application
- **`app.py`** - Your main Flask backend application (ESSENTIAL - DO NOT DELETE)

### 🔄 Database Management
- **`refresh_db.py`** - Resets database with fresh test data (USEFUL - KEEP)
  - Use when: You want to start fresh or reset test data

---

## 🔐 **PASSWORD MANAGEMENT SCRIPTS**

### ✅ Currently Useful
- **`reset_all_passwords.py`** - Sets all user passwords to 'password123' (KEEP)
  - Use when: You want to standardize passwords for testing
  - Status: Working, recently used

### ⚠️ One-Time Use (Can Delete)
- **`rehash_passwords_pbkdf2.py`** - Converted scrypt passwords to pbkdf2 (DELETE - Already done)
  - Purpose: Fixed the login issue by rehashing passwords
  - Status: Job complete, no longer needed

### ⚠️ Verification Scripts (Can Delete)
- **`check_actual_passwords.py`** - Checked password hashes in database (DELETE - Verification done)
- **`verify_password_hashing.py`** - Verified passwords are hashed properly (DELETE - Already confirmed)
- **`test_standard_password.py`** - Tests login with password123 (DELETE - Already tested)
- **`test_all_logins.py`** - Tests all main account logins (DELETE - Already verified)

---

## 🧪 **TESTING SCRIPTS**

### User Management Tests
- **`test_users.py`** - Tests user operations
- **`test_logins.py`** - Tests login functionality  
- **`test_all_cruds.py`** - Tests all CRUD operations
- **`test_create_user_direct.py`** - Tests direct user creation
- **`test_create_user_endpoint.py`** - Tests user creation via API
- **`test_create_with_logging.py`** - Tests user creation with logging
- **`test_create_duplicate.py`** - Tests duplicate user handling
- **`test_cascade_delete.py`** - Tests cascade deletion

### Profile Tests
- **`test_update_profile.py`** - Tests profile update
- **`test_update_profile_api.py`** - Tests profile update API
- **`test_suspend_api.py`** - Tests account suspension

### Feature Tests
- **`test_pin_implementation.py`** - Tests PIN request feature
- **`test_pin_csr_entities.py`** - Tests PIN/CSR entities
- **`test_service_types_api.py`** - Tests service types API
- **`test_service_types_frontend.py`** - Tests service types frontend

**Recommendation:** KEEP if you want automated testing, DELETE if you only test manually

---

## 🔍 **DEBUGGING/CHECKING SCRIPTS**

### Database Schema Checks
- **`check_db_schema.py`** - Checks database schema
- **`check_db_relationships.py`** - Checks table relationships
- **`check_supabase_schema.py`** - Checks Supabase schema
- **`check_fk_constraint.py`** - Checks foreign key constraints
- **`check_service_types.py`** - Checks service types data
- **`check_existing_requests.py`** - Checks existing requests

### Verification Scripts
- **`verify_service_types.py`** - Verifies service types setup
- **`verify_pin_csr_tables.py`** - Verifies PIN/CSR tables
- **`validate_pin_csr_schema.py`** - Validates PIN/CSR schema
- **`validate_schema_comprehensive.py`** - Comprehensive schema validation

### Debug Scripts
- **`debug_login.py`** - Debugs login issues
- **`debug_service_types.py`** - Debugs service types

**Recommendation:** DELETE most of these - they were for one-time debugging. Keep `check_db_schema.py` if you like.

---

## 🛠️ **DATABASE SETUP SCRIPTS**

### One-Time Setup (Can Delete)
- **`add_image_column.py`** - Added image column to requests table (DELETE - Already done)
- **`setup_profiles_table.py`** - Set up profiles table (DELETE - Already done)
- **`setup_pin_csr_tables.py`** - Set up PIN/CSR tables (DELETE - Already done)
- **`setup_pin_csr_direct_sql.py`** - Direct SQL setup for PIN/CSR (DELETE - Already done)
- **`setup_cascade_delete.py`** - Set up cascade delete (DELETE - Already done)

### Data Migration (Can Delete)
- **`update_request_schema.py`** - Updated request schema (DELETE - Already done)
- **`update_routes.py`** - Updated routes (DELETE - Already done)
- **`update_service_types.py`** - Updated service types (DELETE - Already done)

---

## 📊 **UTILITY SCRIPTS**

### Display/Query Scripts
- **`show_active_users.py`** - Shows active users in database
- **`get_pin_user.py`** - Gets PIN user information
- **`delete_test_requests.py`** - Deletes test requests
- **`preflight_check.py`** - Pre-flight system check

**Recommendation:** KEEP `show_active_users.py` and `preflight_check.py`, DELETE the rest

---

## 📁 **DIRECTORIES WITH SCRIPTS**

### `utilities/` folder
- **`utilities/check_db_schema.py`** - Duplicate of root check_db_schema.py (DELETE)

### `src/` folder
Contains your actual application code - **KEEP ALL OF THESE**:
- `src/entity/` - Entity classes (User, Request, Profile, etc.)
- `src/controller/` - Controllers (Auth, UserAccount, UserProfile, etc.)
- `src/utils/` - Utilities (validators, sanitizers, auth middleware, etc.)
- `src/config/` - Configuration files

---

## 🎯 **RECOMMENDED ACTIONS**

### 🗑️ **SAFE TO DELETE (37 scripts)**

**Password Scripts (Already Done):**
1. `rehash_passwords_pbkdf2.py`
2. `check_actual_passwords.py`
3. `verify_password_hashing.py`
4. `test_standard_password.py`
5. `test_all_logins.py`

**Setup Scripts (Already Done):**
6. `add_image_column.py`
7. `setup_profiles_table.py`
8. `setup_pin_csr_tables.py`
9. `setup_pin_csr_direct_sql.py`
10. `setup_cascade_delete.py`
11. `update_request_schema.py`
12. `update_routes.py`
13. `update_service_types.py`

**Debugging Scripts (One-Time Use):**
14. `debug_login.py`
15. `debug_service_types.py`
16. `check_db_relationships.py`
17. `check_supabase_schema.py`
18. `check_fk_constraint.py`
19. `check_service_types.py`
20. `check_existing_requests.py`
21. `verify_service_types.py`
22. `verify_pin_csr_tables.py`
23. `validate_pin_csr_schema.py`
24. `validate_schema_comprehensive.py`
25. `get_pin_user.py`
26. `delete_test_requests.py`

**Test Scripts (If you don't need automated testing):**
27. `test_users.py`
28. `test_logins.py`
29. `test_all_cruds.py`
30. `test_create_user_direct.py`
31. `test_create_user_endpoint.py`
32. `test_create_with_logging.py`
33. `test_create_duplicate.py`
34. `test_cascade_delete.py`
35. `test_update_profile.py`
36. `test_update_profile_api.py`
37. `test_suspend_api.py`
38. `test_pin_implementation.py`
39. `test_pin_csr_entities.py`
40. `test_service_types_api.py`
41. `test_service_types_frontend.py`

**Duplicate Scripts:**
42. `utilities/check_db_schema.py`

### ✅ **KEEP THESE (5-7 scripts)**

**Essential:**
1. `app.py` - Main application (REQUIRED)
2. `refresh_db.py` - Database reset utility (USEFUL)
3. `reset_all_passwords.py` - Password standardization (USEFUL)

**Nice to Have:**
4. `show_active_users.py` - View users in database
5. `preflight_check.py` - System health check
6. `check_db_schema.py` - Check database structure (if you like)

---

## 💡 **SUMMARY**

**Your project has ~50 utility scripts but only needs 3-6 for daily work:**

### Daily Use:
- `app.py` - Run your app
- `refresh_db.py` - Reset data if needed
- `reset_all_passwords.py` - Reset passwords if needed

### Occasional Use:
- `show_active_users.py` - Check users
- `preflight_check.py` - Health check

**The other 40+ scripts were for:**
- One-time database setup ✅ (done)
- Debugging the password issue ✅ (fixed)
- Testing features ✅ (tested)
- Verifying schema ✅ (verified)

**They can all be safely deleted!** Your actual application code is in the `src/` folder, which you should KEEP.

---

## 🚀 **Quick Cleanup Command**

Want me to delete all the unnecessary scripts? Just say "clean up scripts" and I'll remove the 40+ files you don't need anymore!
