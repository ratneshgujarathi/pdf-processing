import pytest
import io
from unittest.mock import patch

def test_list_pdfs(client):
    response = client.get('/api/v1/list')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'pdfs' in response.json['data']
    assert 'count' in response.json['data']

def test_view_pdf_valid(client):
    # First upload a PDF so it exists
    with patch('applications.pdf.api.v1.upload_file_to_s3', return_value=("https://fake-s3-url/test.pdf", None)):
        pdf_bytes = b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF'
        data = {'pdf': (io.BytesIO(pdf_bytes), 'test.pdf')}
        client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
    # Patch boto3 S3 client to return a fake PDF body
    with patch('boto3.client') as mock_boto:
        mock_s3 = mock_boto.return_value
        mock_s3.get_object.return_value = {'Body': io.BytesIO(b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF')}
        response = client.get('/api/v1/view/test.pdf')
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'

def test_view_pdf_not_found(client):
    response = client.get('/api/v1/view/nonexistent.pdf')
    assert response.status_code == 404
    assert response.json['success'] is False
    assert 'PDF not found' in response.json['message']

def test_view_pdf_s3_error(client):
    with patch('boto3.client') as mock_boto:
        mock_s3 = mock_boto.return_value
        mock_s3.get_object.side_effect = Exception('S3 error')
        response = client.get('/api/v1/view/test.pdf')
        assert response.status_code == 500
        assert response.json['success'] is False

def test_list_pdfs_exception(client):
    """Test list when an exception occurs during processing"""
    app = client.application
    with app.app_context():
        with patch('applications.pdf.api.v1.current_app.extensions') as mock_extensions:
            mock_extensions.__getitem__.side_effect = Exception('Test error')
            with app.test_client() as c:
                response = c.get('/api/v1/list')
                assert response.status_code == 500
                assert response.json['success'] is False
                assert 'Failed to retrieve PDFs' in response.json['message']

def test_view_pdf_exception(client):
    """Test view when an exception occurs during processing"""
    app = client.application
    with app.app_context():
        with patch('applications.pdf.api.v1.current_app.extensions') as mock_extensions:
            mock_extensions.__getitem__.side_effect = Exception('Test error')
            with app.test_client() as c:
                response = c.get('/api/v1/view/test.pdf')
                assert response.status_code == 500
                assert response.json['success'] is False
                assert 'Failed to fetch PDF from S3' in response.json['message'] 