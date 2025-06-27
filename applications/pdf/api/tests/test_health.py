def test_health(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['message'] == 'Service is healthy'
    assert isinstance(response.json['data'], dict) 