# 🧪 Test-Driven Development (TDD) - Login Feature

## Overview
This directory contains **pytest-based tests** for the CSR Application, with comprehensive **TDD implementation for the Login Feature** using JSON test data.

---

## 📁 Test Structure

```
tests/
├── __init__.py
├── test_login.py              # ✅ TDD Login Feature Tests (MAIN)
├── test_app.py                # General app tests
├── test_cascade_delete.py     # Cascade delete tests
├── test_password.py           # Password tests
├── test_all_cruds.py          # CRUD operations tests
└── test_data/
    └── login_test_cases.json  # JSON test data for login feature
```

---

## 🎯 Login Feature - TDD Implementation

### Test File: `test_login.py`
Comprehensive test-driven development for login functionality:

**Test Categories:**
1. ✅ **Valid Login Tests** - Successful authentication scenarios
2. ❌ **Invalid Login Tests** - Failed authentication scenarios  
3. 🔍 **Edge Case Tests** - SQL injection, XSS, case sensitivity
4. 🔐 **Token Validation Tests** - JWT format verification
5. 📋 **Response Format Tests** - API response structure validation

**JSON Test Data:** `test_data/login_test_cases.json`
- 4 valid login scenarios (different roles)
- 6 invalid login scenarios (wrong password, missing fields, etc.)
- 3 edge cases (SQL injection, XSS, case sensitivity)

---

## 🚀 Running Tests

### Run All Tests
```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=src --cov-report=html
```

### Run Login Tests Only
```bash
# Run login feature tests
pytest tests/test_login.py

# Run with detailed output
pytest tests/test_login.py -v

# Run specific test
pytest tests/test_login.py::test_valid_logins -v
```

### Run Tests by Category
```bash
# Run only valid login tests
pytest tests/test_login.py -k "valid" -v

# Run only invalid login tests
pytest tests/test_login.py -k "invalid" -v

# Run only edge case tests
pytest tests/test_login.py -k "edge" -v
```

---

## 📊 Test Coverage

### Login Feature Tests Include:

**✅ Valid Login Scenarios:**
- Admin user login (User Admin role)
- PIN user login (PIN role)
- CSR Representative login (CSR Rep role)
- Platform Manager login (Platform Management role)

**❌ Invalid Login Scenarios:**
- Wrong password
- Non-existent username
- Empty username
- Empty password
- Missing username field
- Missing password field

**🔍 Security Tests:**
- SQL injection protection
- XSS attack protection
- Case-sensitive username validation

**🔐 Token Tests:**
- JWT format validation
- Token presence verification
- User ID in response

**📋 Response Format Tests:**
- Success response structure
- Error response structure
- Required fields validation

---

## 💡 TDD Approach Demonstrated

### 1. Test Data (JSON)
```json
{
  "valid_logins": [
    {
      "test_name": "admin_login_success",
      "username": "admin1",
      "password": "password123",
      "expected_status": 200,
      "expected_role": "User Admin",
      "description": "Admin user should login successfully"
    }
  ]
}
```

### 2. Test Implementation (pytest)
```python
def test_valid_logins(client, test_data):
    """Test all valid login scenarios from JSON"""
    for test_case in test_data['valid_logins']:
        response = client.post('/api/auth/login', json={
            'username': test_case['username'],
            'password': test_case['password']
        })
        assert response.status_code == test_case['expected_status']
```

### 3. Benefits
- ✅ **Data-Driven:** Easy to add new test cases via JSON
- ✅ **Maintainable:** Separate test data from test logic
- ✅ **Comprehensive:** Covers valid, invalid, and edge cases
- ✅ **Automated:** Run all tests with single command
- ✅ **Documentation:** Tests serve as API documentation

---

## 📈 Example Test Output

```bash
$ pytest tests/test_login.py -v

tests/test_login.py::test_valid_logins PASSED                    [ 10%]
tests/test_login.py::test_admin_login_returns_correct_role PASSED [ 20%]
tests/test_login.py::test_pin_user_login_returns_correct_role PASSED [ 30%]
tests/test_login.py::test_invalid_logins PASSED                  [ 40%]
tests/test_login.py::test_wrong_password_returns_401 PASSED      [ 50%]
tests/test_login.py::test_edge_cases PASSED                      [ 60%]
tests/test_login.py::test_sql_injection_protection PASSED        [ 70%]
tests/test_login.py::test_xss_protection PASSED                  [ 80%]
tests/test_login.py::test_token_is_jwt_format PASSED             [ 90%]
tests/test_login.py::test_login_response_has_correct_structure PASSED [100%]

============= 10 passed in 2.5s =============
```

---

## 🔧 Setup Requirements

### Install pytest
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install pytest
pip install pytest pytest-cov
```

### Configuration (Optional)
Create `pytest.ini` in project root:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

---

## 📝 Adding New Test Cases

### Add to JSON file:
```json
{
  "valid_logins": [
    {
      "test_name": "new_user_login",
      "username": "newuser",
      "password": "password123",
      "expected_status": 200,
      "expected_role": "User Role",
      "description": "New user description"
    }
  ]
}
```

Tests will automatically pick up new cases!

---

## ✅ Why This Approach Meets TDD Requirements

1. ✅ **pytest Framework:** Industry-standard Python testing
2. ✅ **JSON Test Data:** Data-driven testing approach
3. ✅ **Login Feature:** Comprehensive coverage of authentication
4. ✅ **Multiple Scenarios:** Valid, invalid, and edge cases
5. ✅ **Automated:** Can run in CI/CD pipelines
6. ✅ **Maintainable:** Easy to add/modify test cases
7. ✅ **Documentation:** Tests document expected behavior

---

## 🎓 For Academic Submission

**TDD Evidence:**
- ✅ Test file: `tests/test_login.py`
- ✅ Test data: `tests/test_data/login_test_cases.json`
- ✅ Framework: pytest
- ✅ Feature: Login authentication
- ✅ Coverage: 17+ test cases
- ✅ Approach: Data-driven with JSON

**Run command for demonstration:**
```bash
pytest tests/test_login.py -v --tb=short
```

This will show all test cases passing with clear output! ✨
