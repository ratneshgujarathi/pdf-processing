from flask import Blueprint, current_app, g
from applications.common.response_factory import ResponseFactory
from applications.common.logger import log_request, log_error
import logging

bp = Blueprint('health', __name__)

@bp.route('/health', methods=['GET'])
@log_request
def health_check():
    """Health check endpoint"""
    try:
        # Log health check
        logging.getLogger('api').info(
            "Health check requested",
            extra={
                'request_id': g.get('request_id'),
                'endpoint': 'health_check'
            }
        )
        
        return ResponseFactory.success(
            message='Service is healthy',
            data={
                'status': 'healthy',
                'service': 'pdf-processing-api',
                'timestamp': '2024-01-01T00:00:00Z'
            }
        )
    except Exception as e:
        log_error(e, {
            'operation': 'health_check',
            'request_id': g.get('request_id')
        })
        return ResponseFactory.error(message='Health check failed', status_code=500)

@bp.route('/dbtest', methods=['GET'])
@log_request
def db_test():
    """Database connection test"""
    try:
        # Log database test
        logging.getLogger('api').info(
            "Database test requested",
            extra={
                'request_id': g.get('request_id'),
                'endpoint': 'db_test'
            }
        )
        
        # Test MongoDB connection
        mongo = current_app.extensions['mongo']
        db = mongo.cx['pdf_engine']
        
        # Simple ping test
        db.command('ping')
        
        # Log successful database test
        logging.getLogger('api').info(
            "Database test successful",
            extra={
                'request_id': g.get('request_id'),
                'endpoint': 'db_test'
            }
        )
        
        return ResponseFactory.success(
            message='Database connection successful',
            data={
                'status': 'connected',
                'database': 'mongodb',
                'timestamp': '2024-01-01T00:00:00Z'
            }
        )
    except Exception as e:
        log_error(e, {
            'operation': 'db_test',
            'request_id': g.get('request_id')
        })
        return ResponseFactory.error(message='Database connection failed', status_code=500) 