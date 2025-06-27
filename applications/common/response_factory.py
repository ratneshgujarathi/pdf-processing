from flask import jsonify

class ResponseFactory:
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        response = {
            "success": True,
            "message": message,
            "data": data if data is not None else {},
        }
        return jsonify(response), status_code

    @staticmethod
    def error(message="An error occurred", status_code=400, errors=None):
        response = {
            "success": False,
            "message": message,
            "errors": errors if errors is not None else {},
        }
        return jsonify(response), status_code 