from flask import Blueprint, request
from ..handlers.common.service import CommonOperation
from helpers.response import ErrorResponse, SuccessResponse
from helpers.logger import LoggerManager


pdf_bp = Blueprint("pdf_bp", __name__)


# Initialize a logger for a specific module (e.g., 'user_module')
pdf_process_logger = LoggerManager(module_name="pdf_process").get_logger()

# Initialize the CommonOperation class
common_ops = CommonOperation(upload_folder="uploads", allowed_extensions={"pdf"})


@pdf_bp.route("/upload", methods=["POST"])
def upload_file():
    try:
        return SuccessResponse(common_ops.upload(request.files))
    except Exception as e:
        pdf_process_logger.error(f"Unexpected error: {e}")
        return ErrorResponse(e.args)
