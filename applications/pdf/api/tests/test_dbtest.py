from unittest.mock import patch

def test_dbtest_success(client):
    with patch('flask_pymongo.wrappers.Database.list_collection_names', return_value=['pdfs']):
        response = client.get('/api/v1/dbtest')
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'collections' in response.json['data']

def test_dbtest_error(client):
    with patch('flask_pymongo.wrappers.Database.list_collection_names', side_effect=Exception('DB error')):
        response = client.get('/api/v1/dbtest')
        assert response.status_code == 500
        assert response.json['success'] is False
        assert 'Database connection failed' in response.json['message']
        assert 'errors' in response.json 