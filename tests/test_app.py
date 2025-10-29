import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app as flask_app

if 'trigger_500_test' not in flask_app.view_functions:
    @flask_app.route('/trigger-500-test')
    def trigger_500_test():
        raise RuntimeError('Boom')


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
    with flask_app.test_client() as client:
        yield client


def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {
        'status': 'healthy',
        'message': 'CSR App Backend is running'
    }


def test_not_found_handler(client):
    response = client.get('/api/nonexistent-endpoint')
    assert response.status_code == 404
    assert response.get_json() == {
        'success': False,
        'message': 'Endpoint not found'
    }


def test_internal_error_handler(client):
    response = client.get('/trigger-500-test')
    assert response.status_code == 500
    assert response.get_json() == {
        'success': False,
        'message': 'Internal server error'
    }
