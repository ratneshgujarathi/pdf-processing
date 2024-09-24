import os
import dotenv
from traceback import format_exc
from helpers.logger import LoggerManager

config_logs = LoggerManager('config').get_logger()


dotenv.load_dotenv()

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit uploads to 16MB
    MONGO_URI = "mongodb://localhost:27017"

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'
    MONGO_URI = os.environ.get('MONGO_URI_DEV')

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key')
    MONGO_URI = os.environ.get('MONGO_URI_PROD')

class TestingConfig(Config):
    TESTING = True
    
    
def load_config():
    try:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'dev' or env == 'development':
            return DevelopmentConfig
        elif env == 'test' or env == 'testing':
            return TestingConfig
        else:
            return ProductionConfig
    except Exception as e:
        print(format_exc())
        config_logs.log(1, e.args, exc_info=True, stack_info=True)
        
        