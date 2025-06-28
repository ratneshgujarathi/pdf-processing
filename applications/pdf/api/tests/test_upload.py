import io
from unittest.mock import patch
import hashlib
import pytest

def test_upload_pdf(client):
    with patch('applications.pdf.api.v1.upload_file_to_s3', return_value=("https://fake-s3-url/test.pdf", None)):
        pdf_bytes = b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF'
        data = {'pdf': (io.BytesIO(pdf_bytes), 'test.pdf')}
        response = client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 201
        assert response.json['success'] is True
        # Check that filename contains timestamp and original name
        filename = response.json['data']['filename']
        assert filename.endswith('_test.pdf')
        assert len(filename) > len('test.pdf')  # Should have timestamp prefix
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
    assert 'No file part' in response.json['message']

def test_upload_pdf_non_pdf(client):
    data = {'pdf': (io.BytesIO(b'not a pdf'), 'test.txt')}
    response = client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'Only PDF files are allowed' in response.json['message']

def test_upload_pdf_no_filename(client):
    data = {'pdf': (io.BytesIO(b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF'), '')}
    response = client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'No selected file' in response.json['message']

def test_upload_pdf_exception(client):
    """Test upload when an exception occurs during processing"""
    with patch('applications.pdf.api.v1.secure_filename', side_effect=Exception('Test error')):
        pdf_bytes = b'%PDF-1.4\n%Fake PDF file for testing\n%%EOF'
        data = {'pdf': (io.BytesIO(pdf_bytes), 'test.pdf')}
        response = client.post('/api/v1/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 500
        assert response.json['success'] is False
        assert 'Upload failed' in response.json['message']

def test_s3_utils_error_handling():
    """Test S3 utility functions error handling directly"""
    from applications.common.s3_utils import upload_file_to_s3, generate_presigned_url
    
    # Test upload_file_to_s3 error handling
    with patch('applications.common.s3_utils.s3_client') as mock_s3:
        mock_s3.upload_fileobj.side_effect = Exception('Upload error')
        mock_file = io.BytesIO(b'test content')
        url, error = upload_file_to_s3(mock_file, 'test.pdf', 'application/pdf')
        assert url is None
        assert error == 'Upload error'
    
    # Test generate_presigned_url error handling
    with patch('applications.common.s3_utils.s3_client') as mock_s3:
        mock_s3.generate_presigned_url.side_effect = Exception('URL error')
        url, error = generate_presigned_url('test.pdf')
        assert url is None
        assert error == 'URL error'

def test_s3_utils_success():
    """Test S3 utility functions success paths directly"""
    from applications.common.s3_utils import upload_file_to_s3, generate_presigned_url
    import io
    with patch('applications.common.s3_utils.s3_client') as mock_s3:
        mock_s3.upload_fileobj.return_value = None
        url, error = upload_file_to_s3(io.BytesIO(b'test'), 'test.pdf', 'application/pdf')
        assert url is not None
        assert error is None
        mock_s3.generate_presigned_url.return_value = 'http://example.com/test.pdf'
        url, error = generate_presigned_url('test.pdf')
        assert url == 'http://example.com/test.pdf'
        assert error is None 