from flask import Flask
import os
import logging
from logging.handlers import RotatingFileHandler
from config import load_config

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    config_class = load_config()

    # Load the config from config.py
    app.config.from_object(config_class)
    
    # Load config from instance folder (instance/config.py)
    # app.config.from_pyfile('config.py', silent=True)
    # Setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')

    # Register the routes (API endpoints)
    from .pdf.api.v1 import pdf_bp
    app.register_blueprint(pdf_bp, url_prefix='/api/pdf')

    return app