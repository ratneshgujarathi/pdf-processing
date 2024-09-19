import logging
from flask import Response, send_file
from flask.json import dumps
from constants.response import RESPONSE_CONSTANTS


class CoreResponse():

    @staticmethod
    def json(response, status, mimetype='application/json'):
        return Response(
            response=dumps(response),
            status=status,
            mimetype=mimetype
        )

    @staticmethod
    def file(file_content, file_name, mimetype='application/zip'):
        return send_file(
            file_content,
            mimetype=mimetype,
            as_attachment=True,
            attachment_filename=file_name
        )


class SuccessResponse():

    def __new__(cls, payload=None, status_code=200):

        response = {
            'status': 'success',
            'result': payload
        }

        return CoreResponse.json(response, status_code)


class ErrorResponse():

    def __new__(cls, args):
        format_kwargs = {}
        error = {}
        try:
            types = args[0]
            error_format = RESPONSE_CONSTANTS[types]
            if len(args) > 1:
                format_kwargs = {'field': args[1]}
                error['field'] = args[1]
        except Exception as err:
            logging.info(cls)
            logging.info(args)
            logging.error(f'Error while building response: {err}')
            types = 'INTERNAL_SERVER_ERROR'
            format_kwargs = {}
            error_format = RESPONSE_CONSTANTS[types]

        error['error_code'] = types
        error['message'], status_code = error_format(**format_kwargs)

        response = {
            'error': error,
            'status': 'error'
        }

        return CoreResponse.json(response, status_code)