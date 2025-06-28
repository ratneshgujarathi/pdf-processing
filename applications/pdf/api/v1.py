from flask import Blueprint, jsonify, current_app, request, Response, g
from werkzeug.utils import secure_filename
from bson import ObjectId
import os
from applications.common.response_factory import ResponseFactory
from flasgger import swag_from
from applications.common.s3_utils import upload_file_to_s3, generate_presigned_url
import boto3
import hashlib
from datetime import datetime, timezone
from applications.common.logger import log_request, log_pdf_operation, log_error
import logging

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
@swag_from(os.path.join(os.path.dirname(__file__), '../specs/upload.yaml'))
@log_request
def upload_pdf():
    """Upload a PDF file to S3 and store metadata in MongoDB"""
    try:
        if 'pdf' not in request.files:
            log_pdf_operation('upload', error='No file part in the request', request_id=g.get('request_id'))
            return ResponseFactory.error(message='No file part in the request', status_code=400)
        file = request.files['pdf']
        filename = file.filename or ''
        if filename == '':
            log_pdf_operation('upload', error='No selected file', request_id=g.get('request_id'))
            return ResponseFactory.error(message='No selected file', status_code=400)
        if not filename.lower().endswith('.pdf'):
            log_pdf_operation('upload', error='Only PDF files are allowed', pdf_filename=filename, request_id=g.get('request_id'))
            return ResponseFactory.error(message='Only PDF files are allowed', status_code=400)

        # Secure filename
        safe_filename = secure_filename(filename)
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{safe_filename}"

        # Get file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        # Log upload attempt
        log_pdf_operation('upload', 
                         pdf_filename=filename,
                         unique_filename=safe_filename,
                         file_size=file_size,
                         request_id=g.get('request_id'))

        # Upload to S3
        file_url, error = upload_file_to_s3(file, safe_filename, file.content_type)
        if error:
            log_error(error, {
                'operation': 'upload',
                'request_id': g.get('request_id'),
                'pdf_filename': filename
            })
            return ResponseFactory.error(message='Failed to upload PDF to S3', status_code=500, errors={'exception': error})

        # Store metadata in MongoDB
        mongo = current_app.extensions['mongo']
        db = mongo.cx['pdf_engine']
        now = datetime.now(timezone.utc)
        
        db.pdfs.insert_one({
            'filename': safe_filename,
            'original_filename': filename,
            'content_type': file.content_type,
            'size': file_size,
            'md5': hashlib.md5(file.read()).hexdigest(),
            'created_at': now,
            'updated_at': now,
        })
        log_pdf_operation('upload', 
                         success=True,
                         pdf_filename=filename,
                         unique_filename=safe_filename,
                         file_size=file_size,
                         mongo_id=str(ObjectId(db.pdfs.find_one({'filename': safe_filename})['_id'])),
                         request_id=g.get('request_id'))
        return ResponseFactory.success(
            data={'filename': safe_filename},
            message='PDF uploaded successfully',
            status_code=201
        )
    except Exception as e:
        log_error(e, {
            'operation': 'upload',
            'request_id': g.get('request_id'),
            'pdf_filename': filename if 'filename' in locals() else 'unknown'
        })
        return ResponseFactory.error(message='Upload failed', status_code=500)

@api_bp.route('/list', methods=['GET'])
@swag_from(os.path.join(os.path.dirname(__file__), '../specs/list_pdfs.yaml'))
@log_request
def list_pdfs():
    """List all uploaded PDFs with metadata"""
    try:
        mongo = current_app.extensions['mongo']
        db = mongo.cx['pdf_engine']
        pdfs = list(db.pdfs.find({}))
        
        # Convert ObjectId to string and remove S3 URLs
        for pdf in pdfs:
            pdf['_id'] = str(pdf['_id'])
            pdf.pop('s3_url', None)
            pdf['view_path'] = f"/api/v1/view/{pdf['filename']}"
            # Handle datetime conversion safely
            if 'created_at' in pdf and hasattr(pdf['created_at'], 'isoformat'):
                pdf['created_at'] = pdf['created_at'].isoformat()
            if 'updated_at' in pdf and hasattr(pdf['updated_at'], 'isoformat'):
                pdf['updated_at'] = pdf['updated_at'].isoformat()
        log_pdf_operation('list', 
                         count=len(pdfs),
                         request_id=g.get('request_id'))
        return ResponseFactory.success(
            data={'pdfs': pdfs, 'count': len(pdfs)},
            message='List of PDFs retrieved successfully.'
        )
    except Exception as e:
        log_error(e, {
            'operation': 'list',
            'request_id': g.get('request_id')
        })
        return ResponseFactory.error(message='Failed to retrieve PDFs', status_code=500)

@api_bp.route('/view/<filename>', methods=['GET'])
@swag_from(os.path.join(os.path.dirname(__file__), '../specs/view.yaml'))
@log_request
def view_pdf(filename):
    """View a specific PDF file"""
    try:
        log_pdf_operation('view', 
                         pdf_filename=filename,
                         request_id=g.get('request_id'))
        mongo = current_app.extensions['mongo']
        db = mongo.cx['pdf_engine']
        
        # Check if PDF exists in database
        pdf_doc = db.pdfs.find_one({'filename': filename})
        if not pdf_doc:
            log_pdf_operation('view', error='PDF not found', pdf_filename=filename, request_id=g.get('request_id'))
            return ResponseFactory.error(message='PDF not found', status_code=404)

        # Get PDF from S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION')
        )
        s3_object = s3_client.get_object(Bucket=os.environ.get('AWS_S3_BUCKET_NAME'), Key=filename)
        log_pdf_operation('view', 
                         success=True,
                         pdf_filename=filename,
                         request_id=g.get('request_id'))
        return Response(
            s3_object['Body'].read(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'inline; filename={filename}'}
        )
    except Exception as e:
        log_error(e, {
            'operation': 'view',
            'pdf_filename': filename,
            'request_id': g.get('request_id')
        })
        return ResponseFactory.error(message='Failed to fetch PDF from S3', status_code=500, errors={'exception': str(e)}) 