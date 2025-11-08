"""
Test-Driven Development (TDD) for Login Feature
Uses pytest with JSON test data for comprehensive login testing
"""

import os
import sys
import json
import pytest

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    flask_app.config.update({
        'TESTING': True,
        'PROPAGATE_EXCEPTIONS': False
    })
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def test_data():
    """Load test data from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'test_data', 'login_test_cases.json')
    with open(json_path, 'r') as f:
        return json.load(f)


# ==================== VALID LOGIN TESTS ====================

def test_valid_logins(client, test_data):
    """Test all valid login scenarios from JSON test data"""
    for test_case in test_data['valid_logins']:
        print(f"\n🧪 Testing: {test_case['test_name']} - {test_case['description']}")
        
        # Prepare request payload
        payload = {
            'username': test_case['username'],
            'password': test_case['password'],
            'role_name': test_case['expected_role']
        }
        
        # Make login request
        response = client.post(
            '/api/auth/login',
            json=payload,
            content_type='application/json'
        )
        
        # Assert status code
        assert response.status_code == test_case['expected_status'], \
            f"Expected status {test_case['expected_status']}, got {response.status_code}"
        
        # Assert response structure
        data = response.get_json()
        assert data is not None, "Response should contain JSON data"
        assert 'success' in data, "Response should have 'success' field"
        assert data['success'] is True, "Success should be True for valid login"
        
        # API returns data in 'data' field
        assert 'data' in data, "Response should contain 'data' field"
        response_data = data['data']
        
        # Assert token is present
        assert 'token' in response_data, "Response should contain authentication token"
        assert response_data['token'] is not None, "Token should not be None"
        assert len(response_data['token']) > 0, "Token should not be empty"
        
        # Assert user data is present
        assert 'user' in response_data, "Response should contain user data"
        user = response_data['user']
        assert user['username'] == test_case['username'], \
            f"Username should be {test_case['username']}"
        # Role is an object with 'name' field
        assert user['role']['name'] == test_case['expected_role'], \
            f"Role should be {test_case['expected_role']}"
        
        print(f"✅ PASSED: {test_case['test_name']}")


def test_admin_login_returns_correct_role(client):
    """Test that admin login returns User Admin role"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin1', 'password': 'password123', 'role_name': 'User Admin'},
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['user']['role']['name'] == 'User Admin'


def test_pin_user_login_returns_correct_role(client):
    """Test that PIN user login returns PIN role"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'pin_user1', 'password': 'password123', 'role_name': 'PIN'},
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['user']['role']['name'] == 'PIN'


def test_csr_rep_login_returns_correct_role(client):
    """Test that CSR Rep login returns CSR Rep role"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'csr_rep1', 'password': 'password123', 'role_name': 'CSR Rep'},
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['user']['role']['name'] == 'CSR Rep'


# ==================== INVALID LOGIN TESTS ====================

def test_invalid_logins(client, test_data):
    """Test all invalid login scenarios from JSON test data"""
    for test_case in test_data['invalid_logins']:
        print(f"\n🧪 Testing: {test_case['test_name']} - {test_case['description']}")
        
        # Prepare request payload
        payload = {}
        if test_case['username'] is not None:
            payload['username'] = test_case['username']
        if test_case['password'] is not None:
            payload['password'] = test_case['password']
        # Add role_name for non-empty username cases
        if test_case['username'] and test_case['username'] != '':
            payload['role_name'] = 'User Admin'
        
        # Make login request
        response = client.post(
            '/api/auth/login',
            json=payload,
            content_type='application/json'
        )
        
        # Assert status code
        assert response.status_code == test_case['expected_status'], \
            f"Expected status {test_case['expected_status']}, got {response.status_code}"
        
        # Assert response structure
        data = response.get_json()
        assert data is not None, "Response should contain JSON data"
        assert 'success' in data, "Response should have 'success' field"
        assert data['success'] is False, "Success should be False for invalid login"
        
        # Assert error message
        assert 'message' in data, "Response should contain error message"
        assert test_case['expected_message'] in data['message'], \
            f"Expected message '{test_case['expected_message']}', got '{data['message']}'"
        
        # Assert no token is returned in data field
        if 'data' in data:
            assert 'token' not in data['data'] or data['data'].get('token') is None, \
                "Token should not be present for failed login"
        
        print(f"✅ PASSED: {test_case['test_name']}")


def test_wrong_password_returns_401(client):
    """Test that wrong password returns 401 Unauthorized"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin1', 'password': 'wrongpassword', 'role_name': 'User Admin'},
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid credentials' in data['message'] or 'Invalid username' in data['message']


def test_nonexistent_user_returns_401(client):
    """Test that non-existent user returns 401 Unauthorized"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'nonexistentuser123', 'password': 'password123', 'role_name': 'User Admin'},
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False


def test_empty_credentials_returns_400(client):
    """Test that empty credentials return 400 Bad Request"""
    response = client.post(
        '/api/auth/login',
        json={'username': '', 'password': '', 'role_name': ''},
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


# ==================== EDGE CASE TESTS ====================

def test_edge_cases(client, test_data):
    """Test edge cases from JSON test data"""
    for test_case in test_data['edge_cases']:
        print(f"\n🧪 Testing: {test_case['test_name']} - {test_case['description']}")
        
        # Prepare request payload
        payload = {
            'username': test_case['username'],
            'password': test_case['password'],
            'role_name': 'User Admin'
        }
        
        # Make login request
        response = client.post(
            '/api/auth/login',
            json=payload,
            content_type='application/json'
        )
        
        # Assert status code
        assert response.status_code == test_case['expected_status'], \
            f"Expected status {test_case['expected_status']}, got {response.status_code}"
        
        # Assert response structure
        data = response.get_json()
        assert data is not None, "Response should contain JSON data"
        assert 'success' in data, "Response should have 'success' field"
        
        # For 200 responses, success should be True; for others, False
        if test_case['expected_status'] == 200:
            assert data['success'] is True, "Success should be True for valid edge case login"
        else:
            assert data['success'] is False, "Success should be False for invalid edge cases"
        
        print(f"✅ PASSED: {test_case['test_name']}")


def test_sql_injection_protection(client):
    """Test that SQL injection attempts are safely handled"""
    malicious_payloads = [
        "admin' OR '1'='1",
        "admin'--",
        "admin' /*",
        "' OR 1=1--"
    ]
    
    for payload in malicious_payloads:
        response = client.post(
            '/api/auth/login',
            json={'username': payload, 'password': 'password123', 'role_name': 'User Admin'},
            content_type='application/json'
        )
        
        # Should return 400 (validation error) or 401 (auth failed)
        assert response.status_code in [400, 401], \
            f"SQL injection attempt should return 400 or 401, got {response.status_code}"
        data = response.get_json()
        assert data['success'] is False


def test_xss_protection(client):
    """Test that XSS attempts are safely handled"""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "javascript:alert('xss')"
    ]
    
    for payload in xss_payloads:
        response = client.post(
            '/api/auth/login',
            json={'username': payload, 'password': 'password123', 'role_name': 'User Admin'},
            content_type='application/json'
        )
        
        # Should return 400 (validation error) or 401 (auth failed)
        assert response.status_code in [400, 401], \
            f"XSS attempt should return 400 or 401, got {response.status_code}"
        data = response.get_json()
        assert data['success'] is False


def test_case_sensitive_username(client):
    """Test that usernames are NOT case-sensitive (Supabase default behavior)"""
    # Try uppercase version of valid username
    response = client.post(
        '/api/auth/login',
        json={'username': 'ADMIN1', 'password': 'password123', 'role_name': 'User Admin'},
        content_type='application/json'
    )
    
    # Supabase defaults to case-insensitive username matching
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


# ==================== TOKEN VALIDATION TESTS ====================

def test_token_is_jwt_format(client):
    """Test that returned token is in JWT format"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin1', 'password': 'password123', 'role_name': 'User Admin'},
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    token = data['data']['token']
    
    # JWT has 3 parts separated by dots
    parts = token.split('.')
    assert len(parts) == 3, "Token should be in JWT format (3 parts)"


def test_successful_login_contains_user_id(client):
    """Test that successful login response contains user ID"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin1', 'password': 'password123', 'role_name': 'User Admin'},
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert 'user' in data['data']
    assert 'id' in data['data']['user']
    assert isinstance(data['data']['user']['id'], int)


# ==================== RESPONSE FORMAT TESTS ====================

def test_login_response_has_correct_structure(client):
    """Test that login response has the expected structure"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin1', 'password': 'password123', 'role_name': 'User Admin'},
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Check all required top-level fields
    required_fields = ['success', 'message', 'data']
    for field in required_fields:
        assert field in data, f"Response should contain '{field}' field"
    
    # Check data object structure
    data_fields = ['token', 'user']
    for field in data_fields:
        assert field in data['data'], f"Data object should contain '{field}' field"
    
    # Check user object structure
    user_fields = ['id', 'username', 'role']
    for field in user_fields:
        assert field in data['data']['user'], f"User object should contain '{field}' field"


def test_failed_login_response_has_correct_structure(client):
    """Test that failed login response has the expected structure"""
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin1', 'password': 'wrongpassword', 'role_name': 'User Admin'},
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = response.get_json()
    
    # Check required fields for error response
    assert 'success' in data
    assert 'message' in data
    assert data['success'] is False
    # Error responses don't have 'data' field with token
    assert 'data' not in data or 'token' not in data.get('data', {})


# ==================== SUMMARY TEST ====================

def test_login_feature_summary(client, test_data):
    """
    Summary test that validates the entire login feature
    This demonstrates TDD approach with comprehensive test coverage
    """
    print("\n" + "="*60)
    print("🎯 LOGIN FEATURE - TDD COMPREHENSIVE TEST SUMMARY")
    print("="*60)
    
    total_tests = (
        len(test_data['valid_logins']) +
        len(test_data['invalid_logins']) +
        len(test_data['edge_cases'])
    )
    
    print(f"📊 Total test cases from JSON: {total_tests}")
    print(f"   ✅ Valid login cases: {len(test_data['valid_logins'])}")
    print(f"   ❌ Invalid login cases: {len(test_data['invalid_logins'])}")
    print(f"   🔍 Edge cases: {len(test_data['edge_cases'])}")
    print("="*60)
    
    # This assertion always passes - it's just for summary
    assert total_tests > 0, "Test data should contain test cases"
