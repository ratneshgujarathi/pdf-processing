import pytest
from unittest.mock import patch

def test_dbtest_success(client):
    with patch('flask_pymongo.wrappers.Database.command', return_value={'ok': 1}):
        response = client.get('/api/v1/dbtest')
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'database' in response.json['data']
        assert response.json['data']['database'] == 'mongodb'

def test_dbtest_error(client):
    with patch('flask_pymongo.wrappers.Database.command', side_effect=Exception('DB error')):
        response = client.get('/api/v1/dbtest')
        assert response.status_code == 500
        assert response.json['success'] is False
        assert 'Database connection failed' in response.json['message']
        assert 'errors' in response.json 