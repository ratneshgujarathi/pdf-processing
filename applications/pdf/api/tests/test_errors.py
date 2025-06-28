import pytest

def test_404_error(client):
    response = client.get('/api/v1/nonexistent')
    assert response.status_code == 404
    assert response.json['success'] is False
    assert 'not found' in response.json['message'].lower()

def test_405_error(client):
    response = client.post('/api/v1/health')  # POST to GET-only endpoint
    assert response.status_code == 405
    assert response.json['success'] is False
    assert 'method' in response.json['message'].lower()

def test_500_error(client):
    app = client.application
    @app.route('/api/v1/raise-error')
    def raise_error():
        raise Exception("Simulated server error")
    response = client.get('/api/v1/raise-error')
    assert response.status_code == 500
    assert 'error' in response.json
    assert response.json['error'] == 'Internal server error' 