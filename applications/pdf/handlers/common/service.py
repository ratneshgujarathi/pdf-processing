from app import BASE_PATH
import os
from werkzeug.utils import secure_filename
from flask import send_file
from constants.db_constants import CollectionNames
import app as MongoService
from flask_pymongo import ObjectId

class CommonOperation:
    def __init__(self, upload_folder="uploads", allowed_extensions=None):
        if allowed_extensions is None:
            allowed_extensions = {'pdf'}
        self.allowed_extensions = allowed_extensions
        self.upload_folder = os.path.join(BASE_PATH, f"{upload_folder}")

        # Ensure the upload folder exists
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def allowed_file(self, filename):
        """Check if the uploaded file has an allowed extension."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def upload(self, request):
        """Upload a file to the server."""
        # Check if the file part is in the request
        if 'file' not in request.files:
            raise Exception('FILE_NOT_EXIST')

        file = request.files['file']
        
        # Check if the file has a valid name
        if file.filename == '':
            raise Exception('FILE_NAME_INVALID')

        # Return success response with the uploaded file name
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            file_response = MongoService.mongo.db[CollectionNames.FILES].insert_one({"filepath": file_path,  "filename": filename})
            if not file_response.acknowledged:
                raise Exception('DB_WRITE_ERROR')
            return {"message": "File uploaded successfully", "file_path": file_path, "file_id": file_response.inserted_id.__str__()}
        else:
            raise Exception('FILE_NOT_ALLOWED')

    def download(self, request):
        """Download a file from the server."""
        id =  request.args.get("id", "")
        file_path_resp = MongoService.mongo.db[CollectionNames.FILES].find_one({"_id": ObjectId(id)})
        filename = file_path_resp.get("filename", "")
        file_path = None
        if filename:
            file_path = os.path.join(self.upload_folder, filename)
        else:
            raise Exception('NOT_FOUND')
        if os.path.exists(file_path):
            return {"file_content": file_path, "file_name": filename}
        else:
            raise Exception('FILE_NOT_FOUND')

    def list_files(self):
        """List all files in the upload directory."""
        files = os.listdir(self.upload_folder)
        return {"files": files}, 200
