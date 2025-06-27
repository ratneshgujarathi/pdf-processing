import io
from unittest.mock import patch
import hashlib

def test_upload_pdf(client):
    with patch('applications.pdf.api.v1.upload_file_to_s3', return_value=("https://fake-s3-url/test.pdf", None)):
        pdf_bytes = b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF'
        data = {'pdf': (io.BytesIO(pdf_bytes), 'test.pdf')}
        response = client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 201
        assert response.json['success'] is True
        assert response.json['data']['filename'] == 'test.pdf'
        # Check metadata in list
        with patch('boto3.client') as mock_boto:
            mock_s3 = mock_boto.return_value
            mock_s3.get_object.return_value = {'Body': io.BytesIO(pdf_bytes)}
            list_response = client.get('/api/v1/list')
            pdfs = list_response.json['data']['pdfs']
            found = False
            for pdf in pdfs:
                if pdf['filename'] == 'test.pdf':
                    found = True
                    assert pdf['original_filename'] == 'test.pdf'
                    assert pdf['content_type'] == 'application/pdf'
                    assert pdf['size'] == len(pdf_bytes)
                    assert pdf['md5'] == hashlib.md5(pdf_bytes).hexdigest()
                    assert 'created_at' in pdf
                    assert 'updated_at' in pdf
            assert found

def test_upload_pdf_s3_error(client):
    with patch('applications.pdf.api.v1.upload_file_to_s3', return_value=(None, "S3 error")):
        pdf_bytes = b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF'
        data = {'pdf': (io.BytesIO(pdf_bytes), 'test.pdf')}
        response = client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 500
        assert response.json['success'] is False
        assert 'Failed to upload PDF to S3' in response.json['message']

def test_upload_pdf_missing_file(client):
    response = client.post('/api/v1/upload', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'No file part in the request' in response.json['message']

def test_upload_pdf_non_pdf(client):
    data = {'pdf': (io.BytesIO(b'not a pdf'), 'test.txt')}
    response = client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'Only PDF files are allowed' in response.json['message']

def test_upload_pdf_no_filename(client):
    data = {'pdf': (io.BytesIO(b''), '')}
    response = client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'No selected file' in response.json['message'] 