from flask import Flask, g, request
from flask_pymongo import PyMongo
from flask_cors import CORS
import uuid
from .config import Config
from dotenv import load_dotenv
from flasgger import Swagger
from applications.common.response_factory import ResponseFactory
from applications.common.logger import setup_logging, log_error

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['PROPAGATE_EXCEPTIONS'] = False
    
    # Setup logging
    loggers = setup_logging(app)
    app.config['LOGGERS'] = loggers
    
    # Enable CORS
    CORS(app)
    
    # Request ID middleware
    @app.before_request
    def before_request():
        """Add request ID to each request"""
        g.request_id = str(uuid.uuid4())
        app.logger.info(f"Request started: {request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Log request completion"""
        app.logger.info(f"Request completed: {request.method} {request.path} - Status: {response.status_code}")
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler with logging"""
        log_error(e, {
            'request_id': g.get('request_id', 'unknown'),
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path
        })
        return {'error': 'Internal server error'}, 500
    
    mongo = PyMongo(app)
    app.extensions['mongo'] = mongo

    from .swagger_config import swagger_template, swagger_config
    Swagger(app, template=swagger_template, config=swagger_config)

    from .api.v1 import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    from .api.health import bp as health_bp
    app.register_blueprint(health_bp, url_prefix='/api/v1')

    @app.errorhandler(404)
    def not_found_error(error):
        return ResponseFactory.error(
            message="The requested resource was not found.",
            status_code=404
        )

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return ResponseFactory.error(
            message="The method is not allowed for the requested URL.",
            status_code=405
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return ResponseFactory.error(
            message="An internal server error occurred.",
            status_code=500
        )

    return app 