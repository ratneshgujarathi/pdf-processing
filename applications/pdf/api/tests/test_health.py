import pytest
from unittest.mock import patch

def test_health(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['data']['status'] == 'healthy'

def test_health_exception(client):
    """Test health check when an exception occurs"""
    with patch('applications.common.response_factory.ResponseFactory.success', side_effect=Exception('Test error')):
        response = client.get('/api/v1/health')
        assert response.status_code == 500
        assert response.json['success'] is False
        assert 'Health check failed' in response.json['message'] 