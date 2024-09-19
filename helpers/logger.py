import os
import logging
from logging.handlers import RotatingFileHandler

class LoggerManager:
    def __init__(self, module_name, log_folder='logs', max_bytes=5 * 1024 * 1024, backup_count=5, log_level=logging.DEBUG):
        """
        Initialize the logger for the given module name.
        
        Parameters:
        - module_name: The name of the module for which the logger is being created.
        - log_folder: The base folder where logs will be stored.
        - max_bytes: Maximum size of a log file before it gets rotated.
        - backup_count: Number of backup log files to keep.
        - log_level: Logging level (default is DEBUG).
        """
        # Create log directory based on the module name
        self.log_folder = os.path.join(log_folder, module_name)
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
        
        # Create the logger for the module
        self.logger = logging.getLogger(module_name)
        self.logger.setLevel(log_level)

        # Create a rotating file handler
        log_file = os.path.join(self.log_folder, f'{module_name}.log')
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        
        # Set the formatter
        self.set_formatter(file_handler)
        
        # Add the handler to the logger
        if not self.logger.handlers:  # Avoid adding multiple handlers if already configured
            self.logger.addHandler(file_handler)

    def set_formatter(self, handler):
        """Set a custom formatter for log messages."""
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s'
        )
        handler.setFormatter(formatter)

    def get_logger(self):
        """Return the logger instance."""
        return self.logger

# Core Logger for API hits
class CoreLogger(LoggerManager):
    def __init__(self, log_folder='logs/core', log_level=logging.DEBUG):
        super().__init__(module_name='core', log_folder=log_folder, log_level=log_level)

    def log_api_hit(self, endpoint, method, status_code):
        """Log each API hit with its details."""
        message = f'API hit: {method} {endpoint} - Status: {status_code}'
        self.logger.info(message)
