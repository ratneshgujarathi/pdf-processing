import pytest
import io
from unittest.mock import patch, MagicMock

def test_list_pdfs(client):
    mock_collection = client.application.extensions['mongo'].cx['pdf_engine'].pdfs
    mock_collection.find.return_value = []
    response = client.get('/api/v1/list')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'pdfs' in response.json['data']
    assert 'count' in response.json['data']

def test_view_pdf_valid(client):
    mock_collection = client.application.extensions['mongo'].cx['pdf_engine'].pdfs
    mock_pdf_doc = {
        'filename': 'test.pdf',
        'original_filename': 'test.pdf',
        'content_type': 'application/pdf',
        'size': 100,
        'md5': 'test_md5',
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }
    mock_collection.find_one.return_value = mock_pdf_doc
    with patch('boto3.client') as mock_boto:
        mock_s3 = mock_boto.return_value
        mock_s3.get_object.return_value = {'Body': io.BytesIO(b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF')}
        response = client.get('/api/v1/view/test.pdf')
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'

def test_view_pdf_not_found(client):
    mock_collection = client.application.extensions['mongo'].cx['pdf_engine'].pdfs
    mock_collection.find_one.return_value = None
    
    # Mock S3 client to prevent real calls and verify the 404 path
    with patch('boto3.client') as mock_boto:
        mock_s3 = mock_boto.return_value
        # This should not be called if the DB returns None, but let's mock it just in case
        mock_s3.get_object.return_value = {'Body': io.BytesIO(b'fake content')}
        
        response = client.get('/api/v1/view/nonexistent.pdf')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_data(as_text=True)}")
        
        assert response.status_code == 404
        assert response.json['success'] is False
        assert 'PDF not found' in response.json['message']

def test_view_pdf_s3_not_found(client):
    """Test when PDF exists in MongoDB but not in S3"""
    mock_collection = client.application.extensions['mongo'].cx['pdf_engine'].pdfs
    mock_pdf_doc = {
        'filename': 'test.pdf',
        'original_filename': 'test.pdf',
        'content_type': 'application/pdf',
        'size': 100,
        'md5': 'test_md5',
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }
    mock_collection.find_one.return_value = mock_pdf_doc
    
    # Mock S3 client to raise an error
    with patch('boto3.client') as mock_boto:
        mock_s3 = mock_boto.return_value
        mock_s3.get_object.side_effect = Exception('An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist.')
        response = client.get('/api/v1/view/test.pdf')
        assert response.status_code == 500
        assert response.json['success'] is False

def test_view_pdf_s3_error(client):
    mock_collection = client.application.extensions['mongo'].cx['pdf_engine'].pdfs
    mock_pdf_doc = {
        'filename': 'test.pdf',
        'original_filename': 'test.pdf',
        'content_type': 'application/pdf',
        'size': 100,
        'md5': 'test_md5',
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }
    mock_collection.find_one.return_value = mock_pdf_doc
    with patch('boto3.client') as mock_boto:
        mock_s3 = mock_boto.return_value
        mock_s3.get_object.side_effect = Exception('S3 error')
        response = client.get('/api/v1/view/test.pdf')
        assert response.status_code == 500
        assert response.json['success'] is False

def test_list_pdfs_exception(client):
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
    app = client.application
    with app.app_context():
        with patch('applications.pdf.api.v1.current_app.extensions') as mock_extensions:
            mock_extensions.__getitem__.side_effect = Exception('Test error')
            with app.test_client() as c:
                response = c.get('/api/v1/view/test.pdf')
                assert response.status_code == 500
                assert response.json['success'] is False
                assert 'Failed to fetch PDF from S3' in response.json['message'] 