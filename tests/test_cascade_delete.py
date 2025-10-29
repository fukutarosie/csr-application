import os
import sys
from datetime import datetime

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as client:
        yield client


def login(client):
    response = client.post(
        '/api/auth/login',
        json={'username': 'admin1', 'password': 'password123', 'role_name': 'User Admin'}
    )
    assert response.status_code == 200
    data = response.get_json()
    return data.get('data', {}).get('token') or data.get('token')


def test_cascade_delete(client):
    token = login(client)
    headers = {'Authorization': f'Bearer {token}'}
    timestamp = datetime.now().strftime('%H%M%S')
    role_data = {
        'role_name': f'CASCADE_TEST_ROLE_{timestamp}',
        'role_code': f'CASCADE_TEST_{timestamp}',
        'description': 'Test role for CASCADE DELETE verification'
    }
    response = client.post('/api/roles', json=role_data, headers=headers)
    assert response.status_code == 201
    role = response.get_json()['data']
    role_id = role['id']
    user_ids = []
    for i in range(1, 4):
        user_data = {
            'username': f'cascade_test_user_{timestamp}_{i}',
            'password': 'testpass123',
            'email': f'cascade_test_{timestamp}_{i}@test.com',
            'full_name': f'Cascade Test User {i}',
            'role_id': role_id
        }
        response = client.post('/api/users', json=user_data, headers=headers)
        assert response.status_code == 201
        user = response.get_json()['data']
        user_ids.append(user['id'])
    response = client.get('/api/users', headers=headers)
    assert response.status_code == 200
    all_users = response.get_json().get('data', [])
    assert all(user_id in [u['id'] for u in all_users] for user_id in user_ids)
    response = client.delete(f'/api/roles/{role_id}', headers=headers)
    assert response.status_code == 200
    response = client.get('/api/users', headers=headers)
    assert response.status_code == 200
    all_users_after = response.get_json().get('data', [])
    assert all(user_id not in [u['id'] for u in all_users_after] for user_id in user_ids)
