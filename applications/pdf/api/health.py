from flask import Blueprint, current_app
from applications.common.response_factory import ResponseFactory

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health():
    return ResponseFactory.success(message='Service is healthy')

@health_bp.route('/dbtest', methods=['GET'])
def db_test():
    mongo = current_app.extensions['mongo']
    try:
        # Try listing collections as a test
        collections = mongo.db.list_collection_names()
        return ResponseFactory.success(
            data={'collections': collections},
            message='Database connected',
        )
    except Exception as e:
        return ResponseFactory.error(
            message='Database connection failed',
            status_code=500,
            errors={'exception': str(e)}
        ) 