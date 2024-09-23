from app import BASE_PATH
import os
from werkzeug.utils import secure_filename
from flask import send_file
from constants.db_constants import CollectionNames
import app as MongoService
from flask_pymongo import ObjectId
from datetime import datetime
from ...utils.utilities import paginate
from helpers.common_helper import make_json_serializable


class CommonOperation:
    def __init__(self, upload_folder="uploads", allowed_extensions=None):
        if allowed_extensions is None:
            allowed_extensions = {"pdf"}
        self.allowed_extensions = allowed_extensions
        self.upload_folder = os.path.join(BASE_PATH, f"{upload_folder}")

        # Ensure the upload folder exists
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def allowed_file(self, filename):
        """Check if the uploaded file has an allowed extension."""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        )

    def upload(self, request):
        """Upload a file to the server."""
        # Check if the file part is in the request
        if "file" not in request.files:
            raise Exception("FILE_NOT_EXIST")

        file = request.files["file"]

        # Check if the file has a valid name
        if file.filename == "":
            raise Exception("FILE_NAME_INVALID")

        # Return success response with the uploaded file name
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            file_response = MongoService.mongo.db[CollectionNames.FILES].insert_one(
                {
                    "filepath": file_path,
                    "filename": filename,
                    "created_on": datetime.now(),
                }
            )
            if not file_response.acknowledged:
                raise Exception("DB_WRITE_ERROR")
            return {
                "message": "File uploaded successfully",
                "file_path": file_path,
                "file_id": file_response.inserted_id.__str__(),
            }
        else:
            raise Exception("FILE_NOT_ALLOWED")

    def download(self, request):
        """Download a file from the server."""
        id = request.args.get("id", "")
        file_path_resp = MongoService.mongo.db[CollectionNames.FILES].find_one(
            {"_id": ObjectId(id)}
        )
        filename = file_path_resp.get("filename", "")
        file_path = None
        if filename:
            file_path = os.path.join(self.upload_folder, filename)
        else:
            raise Exception("NOT_FOUND")
        if os.path.exists(file_path):
            return {"file_content": file_path, "file_name": filename}
        else:
            raise Exception("FILE_NOT_FOUND")

    def list_files(self, request):
        """List all files in the upload directory."""
        # pagination params
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))

        if page < 1 or page_size < 1:
            raise Exception("INVALID_PAGINATION")

        # filtering params
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")
        upload_date = request.args.get("created_on")
        filename = request.args.get("filename")

        # sorting parameters
        sort_by = request.args.get("sort_by", "created_on")
        order = request.args.get("order", "asc")

        query = {}

        # Add date filters to the query if present
        if from_date or to_date:
            query["created_on"] = {}
            if from_date:
                try:
                    query["created_on"]["$gte"] = datetime.strptime(
                        from_date, "%Y-%m-%d"
                    )
                except ValueError:
                    raise Exception("INVALID_DATE_FORMAT", ["from_date"])
            if to_date:
                try:
                    query["created_on"]["$lte"] = datetime.strptime(to_date, "%Y-%m-%d")
                except ValueError:
                    raise Exception("INVALID_DATE_FORMAT", ["to_date"])

        # Filter by specific upload_date
        if upload_date:
            try:
                query["created_on"]["$lte"] = datetime.strptime(upload_date, "%Y-%m-%d")
            except ValueError:
                raise Exception("INVALID_DATE_FORMAT", ["upload_date"])

        # Search by filename
        if filename:
            query["filename"] = {
                "$regex": filename,
                "$options": "i",
            } 

        files, total_count, page = paginate(
            MongoService.mongo.db[CollectionNames.FILES],
            query,
            page,
            page_size,
            sort_by,
            order,
        )
        files = make_json_serializable(files)
        return {"files": files, "count": total_count, "page": page}
