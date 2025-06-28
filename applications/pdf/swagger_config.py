swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "PDF Processing API",
        "description": "API for uploading and processing PDF files.",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["http", "https"],
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
} 