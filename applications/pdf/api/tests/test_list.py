import io
from unittest.mock import patch

def test_list_pdfs(client):
    response = client.get('/api/v1/list')
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'pdfs' in response.json['data']
    assert isinstance(response.json['data']['pdfs'], list)
    for pdf in response.json['data']['pdfs']:
        assert 'view_path' in pdf
        assert pdf['view_path'].startswith('/api/v1/view/')

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
        assert response.data.startswith(b'%PDF-1.4')

def test_view_pdf_not_found(client):
    response = client.get('/api/v1/view/nonexistent.pdf')
    assert response.status_code == 404
    assert response.json['success'] is False
    assert 'File not found' in response.json['message']

def test_view_pdf_s3_error(client):
    # First upload a PDF so it exists
    with patch('applications.pdf.api.v1.upload_file_to_s3', return_value=("https://fake-s3-url/test2.pdf", None)):
        pdf_bytes = b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF'
        data = {'pdf': (io.BytesIO(pdf_bytes), 'test2.pdf')}
        client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
    # Patch boto3 S3 client to raise an exception
    with patch('boto3.client') as mock_boto:
        mock_s3 = mock_boto.return_value
        mock_s3.get_object.side_effect = Exception("S3 error")
        response = client.get('/api/v1/view/test2.pdf')
        assert response.status_code == 500
        assert response.json['success'] is False
        assert 'Failed to fetch PDF from S3' in response.json['message'] 