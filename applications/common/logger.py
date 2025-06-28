import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json
from functools import wraps
import time
from flask import request, g

class CustomJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request-specific information if available
        request_id = getattr(record, 'request_id', None)
        if request_id:
            log_entry['request_id'] = request_id
            
        user_agent = getattr(record, 'user_agent', None)
        if user_agent:
            log_entry['user_agent'] = user_agent
            
        ip_address = getattr(record, 'ip_address', None)
        if ip_address:
            log_entry['ip_address'] = ip_address
            
        endpoint = getattr(record, 'endpoint', None)
        if endpoint:
            log_entry['endpoint'] = endpoint
            
        method = getattr(record, 'method', None)
        if method:
            log_entry['method'] = method
            
        status_code = getattr(record, 'status_code', None)
        if status_code:
            log_entry['status_code'] = status_code
            
        response_time = getattr(record, 'response_time', None)
        if response_time:
            log_entry['response_time'] = response_time
            
        file_size = getattr(record, 'file_size', None)
        if file_size:
            log_entry['file_size'] = file_size
            
        pdf_filename = getattr(record, 'pdf_filename', None)
        if pdf_filename:
            log_entry['pdf_filename'] = pdf_filename
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_logging(app):
    """Setup logging configuration for the application"""
    
    # Create logs directory structure
    logs_dir = os.path.join(os.getcwd(), 'logs')
    core_logs_dir = os.path.join(logs_dir, 'core')
    api_logs_dir = os.path.join(logs_dir, 'api')
    pdf_logs_dir = os.path.join(logs_dir, 'pdf')
    
    for directory in [logs_dir, core_logs_dir, api_logs_dir, pdf_logs_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Configure root logger (core logs)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Core application logs
    core_handler = RotatingFileHandler(
        os.path.join(core_logs_dir, 'app.log'),
        maxBytes=2*1024*1024,  # 2MB
        backupCount=2
    )
    core_handler.setFormatter(CustomJSONFormatter())
    core_handler.setLevel(logging.INFO)
    root_logger.addHandler(core_handler)
    
    # API logs
    api_logger = logging.getLogger('api')
    api_logger.setLevel(logging.INFO)
    
    api_handler = RotatingFileHandler(
        os.path.join(api_logs_dir, 'api.log'),
        maxBytes=2*1024*1024,  # 2MB
        backupCount=2
    )
    api_handler.setFormatter(CustomJSONFormatter())
    api_logger.addHandler(api_handler)
    
    # PDF API specific logs
    pdf_logger = logging.getLogger('pdf_api')
    pdf_logger.setLevel(logging.INFO)
    
    pdf_handler = RotatingFileHandler(
        os.path.join(pdf_logs_dir, 'pdf_api.log'),
        maxBytes=2*1024*1024,  # 2MB
        backupCount=2
    )
    pdf_handler.setFormatter(CustomJSONFormatter())
    pdf_logger.addHandler(pdf_handler)
    
    # PDF upload specific logs
    upload_logger = logging.getLogger('pdf_upload')
    upload_logger.setLevel(logging.INFO)
    
    upload_handler = RotatingFileHandler(
        os.path.join(pdf_logs_dir, 'upload.log'),
        maxBytes=2*1024*1024,  # 2MB
        backupCount=2
    )
    upload_handler.setFormatter(CustomJSONFormatter())
    upload_logger.addHandler(upload_handler)
    
    # PDF view specific logs
    view_logger = logging.getLogger('pdf_view')
    view_logger.setLevel(logging.INFO)
    
    view_handler = RotatingFileHandler(
        os.path.join(pdf_logs_dir, 'view.log'),
        maxBytes=2*1024*1024,  # 2MB
        backupCount=2
    )
    view_handler.setFormatter(CustomJSONFormatter())
    view_logger.addHandler(view_handler)
    
    # Error logs
    error_logger = logging.getLogger('errors')
    error_logger.setLevel(logging.ERROR)
    
    error_handler = RotatingFileHandler(
        os.path.join(core_logs_dir, 'errors.log'),
        maxBytes=2*1024*1024,  # 2MB
        backupCount=2
    )
    error_handler.setFormatter(CustomJSONFormatter())
    error_logger.addHandler(error_handler)
    
    # Console handler for development
    if app.config.get('FLASK_ENV') == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomJSONFormatter())
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
    
    return {
        'core': root_logger,
        'api': api_logger,
        'pdf_api': pdf_logger,
        'pdf_upload': upload_logger,
        'pdf_view': view_logger,
        'errors': error_logger
    }

def log_request(f):
    """Decorator to log API requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Get request information
        request_id = g.get('request_id', 'unknown')
        user_agent = request.headers.get('User-Agent', 'unknown')
        ip_address = request.remote_addr
        endpoint = request.endpoint
        method = request.method
        
        # Log request start
        logger = logging.getLogger('api')
        logger.info(
            f"Request started: {method} {request.path}",
            extra={
                'request_id': request_id,
                'user_agent': user_agent,
                'ip_address': ip_address,
                'endpoint': endpoint,
                'method': method
            }
        )
        
        try:
            response = f(*args, **kwargs)
            status_code = 200  # Default success status
            
            # Log successful request
            response_time = time.time() - start_time
            logger.info(
                f"Request completed: {method} {request.path}",
                extra={
                    'request_id': request_id,
                    'user_agent': user_agent,
                    'ip_address': ip_address,
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': status_code,
                    'response_time': round(response_time, 3)
                }
            )
            
            return response
            
        except Exception as e:
            # Log error
            response_time = time.time() - start_time
            error_logger = logging.getLogger('errors')
            error_logger.error(
                f"Request failed: {method} {request.path} - {str(e)}",
                extra={
                    'request_id': request_id,
                    'user_agent': user_agent,
                    'ip_address': ip_address,
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': 500,
                    'response_time': round(response_time, 3)
                },
                exc_info=True
            )
            raise
    
    return decorated_function

def log_pdf_operation(operation_type, **kwargs):
    """Log PDF-specific operations"""
    logger = logging.getLogger(f'pdf_{operation_type}')
    
    log_data = {
        'operation': operation_type,
        'timestamp': datetime.now().isoformat(),
        **kwargs
    }
    
    logger.info(f"PDF {operation_type} operation", extra=log_data)

def log_error(error, context=None):
    """Log errors with context"""
    logger = logging.getLogger('errors')
    
    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context or {}
    }
    
    logger.error(f"Application error: {str(error)}", extra=error_data, exc_info=True) 