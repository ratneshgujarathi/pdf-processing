from flask import Flask
from flask_pymongo import PyMongo
from .config import Config
from dotenv import load_dotenv
from flasgger import Swagger
from applications.common.response_factory import ResponseFactory

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['PROPAGATE_EXCEPTIONS'] = False

    mongo = PyMongo(app)
    app.extensions['mongo'] = mongo

    from .swagger_config import swagger_template, swagger_config
    Swagger(app, template=swagger_template, config=swagger_config)

    from .api.v1 import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    from .api.health import health_bp
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