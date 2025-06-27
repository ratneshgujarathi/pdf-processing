def test_dbtest(client):
    response = client.get('/api/v1/dbtest')
    assert response.status_code in (200, 500)
    assert 'success' in response.json
    assert 'message' in response.json
    if response.status_code == 200:
        assert response.json['success'] is True
        assert 'collections' in response.json['data']
    else:
        assert response.json['success'] is False
        assert 'errors' in response.json

from unittest.mock import patch

def test_dbtest_error(client):
    with patch('flask_pymongo.wrappers.Database.list_collection_names', side_effect=Exception('DB error')):
        response = client.get('/api/v1/dbtest')
        assert response.status_code == 500
        assert response.json['success'] is False
        assert 'Database connection failed' in response.json['message']
        assert 'errors' in response.json 