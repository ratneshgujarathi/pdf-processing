from flask import Blueprint, jsonify, current_app, request, Response
from werkzeug.utils import secure_filename
import gridfs
from bson import ObjectId
import os
from applications.common.response_factory import ResponseFactory
from flasgger import swag_from
from applications.common.s3_utils import upload_file_to_s3, generate_presigned_url
import boto3
import hashlib
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/upload', methods=['POST'])
@swag_from('../specs/upload.yaml')
def upload_pdf():
    if 'pdf' not in request.files:
        return ResponseFactory.error(message='No file part in the request', status_code=400)
    file = request.files['pdf']
    filename = file.filename or ''
    if filename == '':
        return ResponseFactory.error(message='No selected file', status_code=400)
    if not filename.lower().endswith('.pdf'):
        return ResponseFactory.error(message='Only PDF files are allowed', status_code=400)

    safe_filename = secure_filename(filename)
    file.stream.seek(0)
    file_bytes = file.read()
    md5 = hashlib.md5(file_bytes).hexdigest()
    file_size = len(file_bytes)
    file.stream.seek(0)  # Reset pointer for upload
    file_url, error = upload_file_to_s3(file, safe_filename, file.content_type)
    if error:
        return ResponseFactory.error(message='Failed to upload PDF to S3', status_code=500, errors={'exception': error})

    now = datetime.utcnow().isoformat() + 'Z'
    mongo = current_app.extensions['mongo']
    db = mongo.cx['pdf_engine']
    db.pdfs.insert_one({
        'filename': safe_filename,
        'original_filename': filename,
        'content_type': file.content_type,
        'size': file_size,
        'md5': md5,
        'created_at': now,
        'updated_at': now,
    })
    return ResponseFactory.success(
        data={'filename': safe_filename},
        message='PDF uploaded successfully',
        status_code=201
    )

@api_bp.route('/list', methods=['GET'])
@swag_from('../specs/list_pdfs.yaml')
def list_pdfs():
    mongo = current_app.extensions['mongo']
    db = mongo.cx['pdf_engine']
    pdfs = list(db.pdfs.find({}, {'_id': 0}))
    for pdf in pdfs:
        pdf.pop('s3_url', None)
        pdf['view_path'] = f"/api/v1/view/{pdf['filename']}"
    return ResponseFactory.success(
        data={'pdfs': pdfs},
        message='List of PDFs retrieved successfully.'
    )

@api_bp.route('/view/<filename>', methods=['GET'])
def view_pdf(filename):
    mongo = current_app.extensions['mongo']
    db = mongo.cx['pdf_engine']
    pdf = db.pdfs.find_one({'filename': filename})
    if not pdf:
        return ResponseFactory.error(message='File not found', status_code=404)
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION')
    )
    try:
        s3_object = s3_client.get_object(Bucket=os.environ.get('AWS_S3_BUCKET_NAME'), Key=filename)
        return Response(
            s3_object['Body'].read(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'inline; filename={filename}'}
        )
    except Exception as e:
        return ResponseFactory.error(message='Failed to fetch PDF from S3', status_code=500, errors={'exception': str(e)}) 