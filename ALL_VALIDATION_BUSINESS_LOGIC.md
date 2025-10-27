# 🔒 Complete Validation Business Logic - Comprehensive Reference

## Overview

All validation business logic is centralized in **`src/utils/validators.py`** (326 lines). Two validator classes handle all input validation:

1. **`Validators`** - General user and authentication data validation
2. **`ProfileValidators`** - User profile-specific validation

---

## 📋 VALIDATORS CLASS - Complete Methods

### 1. **`validate_email(email: str)`**

**Purpose:** Validate email address format and length

**Checks:**
- ✅ Email is not empty/None
- ✅ Email length ≤ 100 characters
- ✅ Email matches RFC 5322 pattern
- ✅ Contains @ symbol and domain

**Regex Pattern:** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

**Valid Examples:**
- `john.doe@example.com` ✓
- `user+tag@domain.co.uk` ✓
- `test.email.123@company.org` ✓

**Invalid Examples:**
- `plainaddress` ✗ (no @)
- `@example.com` ✗ (no local part)
- `john@` ✗ (no domain)
- `john@.com` ✗ (invalid domain)
- Very long email (>100 chars) ✗

**Returns:** `(bool, str)` - `(True, "")` if valid, `(False, error_message)` if invalid

**Error Messages:**
- "Email is required"
- "Email is too long (max 100 characters)"
- "Invalid email format"

---

### 2. **`validate_username(username: str)`**

**Purpose:** Validate username format, length, and allowed characters

**Checks:**
- ✅ Username is not empty/None
- ✅ Length between 3-20 characters (MIN: 3, MAX: 20)
- ✅ Only contains: letters, numbers, hyphens, underscores
- ✅ Matches alphanumeric pattern

**Regex Pattern:** `^[a-zA-Z0-9_-]{3,20}$`

**Valid Examples:**
- `john_doe` ✓
- `user-123` ✓
- `JohnDoe` ✓
- `j0hn_d0e` ✓

**Invalid Examples:**
- `ab` ✗ (too short, < 3)
- `very_long_username_here` ✗ (> 20 chars)
- `john@doe` ✗ (contains @)
- `john doe` ✗ (contains space)
- `john.doe` ✗ (contains period)

**Returns:** `(bool, str)` - `(True, "")` if valid, `(False, error_message)` if invalid

**Error Messages:**
- "Username is required"
- "Username must be at least 3 characters"
- "Username must be at most 20 characters"
- "Username can only contain letters, numbers, hyphens, and underscores"

---

### 3. **`validate_password(password: str, require_special: bool = False)`**

**Purpose:** Validate password strength and complexity requirements

**Checks:**
- ✅ Password is not empty/None
- ✅ Length minimum 8 characters (MAX: 100)
- ✅ Contains at least 1 UPPERCASE letter (A-Z)
- ✅ Contains at least 1 lowercase letter (a-z)
- ✅ Contains at least 1 digit (0-9)
- ✅ Contains special character (optional, if `require_special=True`)

**Strength Requirements:**
- Minimum 8 characters
- Maximum 100 characters
- Mixed case (upper + lower)
- At least one digit

**Special Characters (optional):** `!@#$%^&*()_+-=[]{}|;:,.<>?`

**Valid Examples:**
- `MyPassword123` ✓ (upper, lower, digit)
- `SecurePass99` ✓ (upper, lower, digit)
- `Test@123Password` ✓ (with special char)

**Invalid Examples:**
- `pass` ✗ (too short, < 8)
- `password123` ✗ (no uppercase)
- `PASSWORD123` ✗ (no lowercase)
- `MyPassword` ✗ (no digit)
- `MyPassword123` (with require_special=True) ✗ (no special char)

**Returns:** `(bool, str)` - `(True, "")` if valid, `(False, error_message)` if invalid

**Error Messages:**
- "Password is required"
- "Password must be at least 8 characters"
- "Password is too long (max 100 characters)"
- "Password must contain at least one uppercase letter"
- "Password must contain at least one lowercase letter"
- "Password must contain at least one number"
- "Password must contain at least one special character (!@#$%^&*)"

---

### 4. **`validate_full_name(full_name: str)`**

**Purpose:** Validate full name format and length

**Checks:**
- ✅ Full name is not empty/None
- ✅ Length between 2-100 characters (MIN: 2, MAX: 100)
- ✅ Contains at least one letter (A-Z, a-z)
- ✅ No numbers or special characters required

**Valid Examples:**
- `John Doe` ✓ (2 words, has spaces)
- `Mary-Jane` ✓ (hyphenated name)
- `Jean-Claude` ✓ (French-style name)
- `José García` ✓ (special letters allowed)

**Invalid Examples:**
- `J` ✗ (too short, < 2)
- `A very long name with too many characters exceeding one hundred` ✗ (> 100)
- `12345` ✗ (no letters, only numbers)
- `` ✗ (empty)

**Returns:** `(bool, str)` - `(True, "")` if valid, `(False, error_message)` if invalid

**Error Messages:**
- "Full name is required"
- "Full name must be at least 2 characters"
- "Full name must be at most 100 characters"
- "Full name must contain at least one letter"

---

### 5. **`validate_phone(phone: str)`**

**Purpose:** Validate phone number format and minimum digits

**Checks:**
- ✅ Phone is not empty/None
- ✅ Contains at least 10 digits (after removing separators)
- ✅ Only contains: digits, spaces, hyphens, parentheses, plus sign
- ✅ Matches phone pattern

**Regex Pattern:** `^[0-9\-+\s()]{10,}$`

**Valid Examples:**
- `1234567890` ✓ (10 digits)
- `123-456-7890` ✓ (with hyphens)
- `(123) 456-7890` ✓ (with parentheses)
- `+1 (555) 123-4567` ✓ (international format)
- `+44 20 7946 0958` ✓ (UK format)

**Invalid Examples:**
- `12345` ✗ (only 5 digits, < 10)
- `123abc7890` ✗ (contains letters)
- `(555)` ✗ (only 3 digits)
- `` ✗ (empty)

**Returns:** `(bool, str)` - `(True, "")` if valid, `(False, error_message)` if invalid

**Error Messages:**
- "Phone number is required"
- "Phone number must contain at least 10 digits"
- "Invalid phone number format"

---

### 6. **`validate_role_id(role_id: int)`**

**Purpose:** Validate role ID is a positive integer

**Checks:**
- ✅ Role ID is not empty/None
- ✅ Role ID is an integer type
- ✅ Role ID is positive (> 0)

**Valid Examples:**
- `1` ✓ (admin)
- `2` ✓ (csr_rep)
- `3` ✓ (manager)

**Invalid Examples:**
- `0` ✗ (not positive)
- `-1` ✗ (negative)
- `"1"` ✗ (string, not int)
- `None` ✗ (empty)
- `1.5` ✗ (float, not int)

**Returns:** `(bool, str)` - `(True, "")` if valid, `(False, error_message)` if invalid

**Error Messages:**
- "Role ID is required"
- "Role ID must be a positive integer"

---

### 7. **`validate_user_data(username, password, email, full_name, role_id, phone=None)`**

**Purpose:** Validate ALL user creation data fields at once

**Validates:** All 6 user fields together (bulk validation)

**Checks:**
1. ✅ `username` - via `validate_username()`
2. ✅ `password` - via `validate_password()`
3. ✅ `email` - via `validate_email()`
4. ✅ `full_name` - via `validate_full_name()`
5. ✅ `role_id` - via `validate_role_id()`
6. ✅ `phone` (optional) - via `validate_phone()` if provided

**Returns:** `(bool, str)` - `(True, "")` if ALL valid, `(False, error_message)` if ANY field invalid

**Error Message:** Returns first field error found (short-circuits on first failure)

**Example Usage:**
```python
is_valid, error_msg = Validators.validate_user_data(
    username="john_doe",
    password="MyPassword123",
    email="john@example.com",
    full_name="John Doe",
    role_id=2,
    phone="555-123-4567"
)

if not is_valid:
    print(f"Validation failed: {error_msg}")
```

---

### 8. **`validate_user_update(updates: dict)`**

**Purpose:** Validate user update data (any subset of fields)

**Validates:** Only the fields provided in the dictionary

**Checks:**
- ✅ `updates` dict is not empty
- ✅ If `email` in updates → validate via `validate_email()`
- ✅ If `password` in updates → validate via `validate_password()`
- ✅ If `full_name` in updates → validate via `validate_full_name()`
- ✅ If `role_id` in updates → validate via `validate_role_id()`
- ✅ If `phone` in updates → validate via `validate_phone()`

**Returns:** `(bool, str)` - `(True, "")` if ALL provided fields valid, `(False, error_message)` if ANY invalid

**Example Usage:**
```python
# Update only email and phone
is_valid, error_msg = Validators.validate_user_update({
    'email': 'newemail@example.com',
    'phone': '555-987-6543'
})

# Update only password
is_valid, error_msg = Validators.validate_user_update({
    'password': 'NewPassword456'
})
```

---

## 📋 PROFILEVALIDATORS CLASS - Complete Methods

### 1. **`validate_phone(phone: str)`**

**Purpose:** Profile-specific phone validation

**Checks:**
- ✅ Phone is not empty/None
- ✅ Matches phone pattern: `^[0-9\-+\s()]{10,}$`

**Returns:** `(bool, str)` - `(True, "")` if valid, `(False, error_message)` if invalid

**Error Messages:**
- "Phone number is required"
- "Invalid phone number format"

---

### 2. **`validate_address(address: str)`**

**Purpose:** Validate user profile address

**Checks:**
- ✅ Address is not empty/None
- ✅ Length between 5-200 characters (MIN: 5, MAX: 200)
- ✅ Must contain enough characters to be a real address

**Valid Examples:**
- `123 Main St` ✓
- `456 Oak Avenue, New York, NY 10001` ✓
- `789 Elm Road, Toronto, ON M5H 2N2` ✓

**Invalid Examples:**
- `123` ✗ (too short, < 5)
- `Very long address with way too many characters...` (> 200) ✗
- `` ✗ (empty)

**Returns:** `(bool, str)` - `(True, "")` if valid, `(False, error_message)` if invalid

**Error Messages:**
- "Address is required"
- "Address must be at least 5 characters"
- "Address must be at most 200 characters"

---

### 3. **`validate_profile_data(user_id: int, phone: str, address: str)`**

**Purpose:** Validate ALL profile data fields at once

**Validates:** User ID, phone, and address together

**Checks:**
1. ✅ `user_id` - Must be positive integer
2. ✅ `phone` - via `validate_phone()`
3. ✅ `address` - via `validate_address()`

**Returns:** `(bool, str)` - `(True, "")` if ALL valid, `(False, error_message)` if ANY invalid

**Error Messages:**
- "Valid user ID is required"
- "Phone number is required"
- "Invalid phone number format"
- "Address is required"
- "Address must be at least 5 characters"
- "Address must be at most 200 characters"

**Example Usage:**
```python
is_valid, error_msg = ProfileValidators.validate_profile_data(
    user_id=123,
    phone="555-123-4567",
    address="456 Oak Avenue, New York, NY 10001"
)

if not is_valid:
    print(f"Profile validation failed: {error_msg}")
```

---

## 🎯 Validation Constants (RULES)

All validation rules defined as class constants in `Validators`:

```python
# Email
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Username
USERNAME_PATTERN = r'^[a-zA-Z0-9_-]{3,20}$'
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20

# Password
PASSWORD_MIN_LENGTH = 8

# Full Name
FULL_NAME_MIN_LENGTH = 2
FULL_NAME_MAX_LENGTH = 100

# Phone
PHONE_PATTERN = r'^[0-9\-+\s()]{10,}$'
```

All profile validation rules defined in `ProfileValidators`:

```python
# Phone (Profile)
PHONE_PATTERN = r'^[0-9\-+\s()]{10,}$'

# Address
ADDRESS_MIN_LENGTH = 5
ADDRESS_MAX_LENGTH = 200
```

---

## 🔄 Complete Validation Flow for User Creation

### Step-by-Step Validation Process:

```
1. HTTP Request arrives at CreateUserAccountController
   ↓
2. Extract JSON data
   ↓
3. Required fields validation
   if not all fields present:
     return error (400 Bad Request)
   ↓
4. Individual field validation (using Validators class):
   ├─ validate_username()     → Check length 3-20, alphanumeric
   ├─ validate_password()     → Check strength (upper, lower, digit)
   ├─ validate_email()        → Check format RFC 5322
   ├─ validate_full_name()    → Check length 2-100, has letters
   └─ validate_role_id()      → Check positive integer
   
   if any validation fails:
     return error (400 Bad Request)
   ↓
5. Uniqueness checks (in User entity):
   ├─ User.username_exists()  → Check username unique
   └─ User.email_exists()     → Check email unique
   
   if duplicate found:
     return error (409 Conflict)
   ↓
6. Sanitization (in Sanitizers):
   ├─ Trim whitespace
   ├─ Lowercase email/username
   ├─ Normalize strings
   └─ Safe character handling
   ↓
7. Password hashing + create user
   ↓
8. Return 201 Created with user data
```

---

## 📊 Validation Rules Summary Table

| Field | Min Length | Max Length | Pattern | Required | Type |
|-------|-----------|-----------|---------|----------|------|
| **Email** | - | 100 | RFC 5322 | Yes | String |
| **Username** | 3 | 20 | `[a-zA-Z0-9_-]` | Yes | String |
| **Password** | 8 | 100 | Upper+Lower+Digit | Yes | String |
| **Full Name** | 2 | 100 | At least 1 letter | Yes | String |
| **Phone** | 10 digits | - | `[0-9\-+()\s]` | Optional | String |
| **Role ID** | - | - | Positive int | Yes | Integer |
| **Address** | 5 | 200 | Any chars | Yes | String |

---

## 🛠️ Usage Examples in Controllers

### Example 1: Validate Single Field

```python
from src.utils.validators import Validators

# Validate email
is_valid, error_msg = Validators.validate_email("user@example.com")
if not is_valid:
    return {"error": error_msg}, 400
```

### Example 2: Validate All User Data

```python
# Validate all user creation data
is_valid, error_msg = Validators.validate_user_data(
    username="john_doe",
    password="MyPassword123",
    email="john@example.com",
    full_name="John Doe",
    role_id=2,
    phone="555-123-4567"
)

if not is_valid:
    return {"error": error_msg}, 400
```

### Example 3: Validate User Update (Partial)

```python
# Only validating fields being updated
is_valid, error_msg = Validators.validate_user_update({
    'email': 'newemail@example.com',
    'phone': '555-987-6543'
})

if not is_valid:
    return {"error": error_msg}, 400
```

### Example 4: Validate Profile Data

```python
from src.utils.validators import ProfileValidators

is_valid, error_msg = ProfileValidators.validate_profile_data(
    user_id=123,
    phone="555-123-4567",
    address="456 Oak Avenue"
)

if not is_valid:
    return {"error": error_msg}, 400
```

---

## 📁 File Location & Structure

**File:** `src/utils/validators.py` (326 lines)

**Classes:**
1. `ValidationError` - Custom exception
2. `Validators` - 8 validation methods + 4 class constants
3. `ProfileValidators` - 3 validation methods + 2 class constants

**Import Statement:**
```python
from src.utils.validators import Validators, ProfileValidators
```

---

## 🎁 Key Features

✅ **Centralized** - All validation logic in one file
✅ **Reusable** - Used across all controllers
✅ **Comprehensive** - Validates format, length, strength, uniqueness
✅ **Consistent** - Same rules everywhere
✅ **Clear Error Messages** - User-friendly error feedback
✅ **Type Safe** - Returns tuples with bool and message
✅ **Flexible** - Works with single fields or bulk validation

---

## 📝 Notes

- All validators return `(bool, str)` tuples
- `True, ""` = Valid
- `False, "error message"` = Invalid
- Validators work with the BOUNDARY layer (Controllers)
- Sanitizers clean data before validators run
- Entity layer performs additional checks (uniqueness, etc.)

