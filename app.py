from flask import request
from helpers.logger import CoreLogger, LoggerManager
from applications import create_app
from helpers.database import db_init

import os, sys

# Define the base path of the project
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
if BASE_PATH not in sys.path:
    sys.path.append(BASE_PATH)

app = create_app()
mongo = db_init(app)

# Initialize the core logger for logging API hits
core_logger = CoreLogger().get_logger()


@app.before_request
def log_api():
    """Log every API hit before the request is processed."""
    core_logger.info(f"API hit: {request.method} {request.path}")


@app.route("/")
def entry_point():
    return {"status": "running"}


if __name__ == "__main__":
    app.run(debug=True)
