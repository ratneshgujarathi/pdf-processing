import os

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit uploads to 16MB

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key')

class TestingConfig(Config):
    TESTING = True