RESPONSE_CONSTANTS = {
    'BAD_REQUEST': lambda status_code=400: ('Bad Request !!!', status_code),
    'REQUIRED_FIELD': lambda field, status_code=400: ("{0} field is required".format(', '.join(field)), status_code),
    'METHOD_NOT_ALLOWED': lambda status_code=405: ("The method is not allowed", status_code),
    'INTERNAL_SERVER_ERROR': lambda status_code=500: ('The server was unable to complete your request', status_code),
    'NON_ADMIN_USER': lambda status_code=403: ('User dont have required privileges. please contact administrator', status_code),
    'ACCESS_DENIED': lambda status_code=401: ('User dont have access to the resource. please contact administrator', status_code),

    # Resource CRUD errors, if specific error not defined then we can use from this
    'RESOURCE_ALREADY_EXISTS': lambda status_code=409: ('Resource already exists', status_code),
    'RESOURCE_NOT_FOUND': lambda status_code=409: ('The resource not found, it might be might be partially or completly deleted from system.', status_code),
    'RESOURCE_NOT_CREATED': lambda status_code=409: ('Failed to create', status_code),
    'RESOURCE_NOT_UPDATED': lambda status_code=409: ('Failed to update', status_code),
    'RESOURCE_NOT_DELETED': lambda status_code=409: ('Failed to delete', status_code),

    # Login
    'UNAUTHORIZED': lambda status_code=401: ('Authentication Failed.', status_code),
    'UNAUTHORIZED_FORBIDDEN': lambda status_code=403: ('Authentication Forbidden.', status_code),
    'INVALID_SECURITY_ANSWER': lambda status_code=401: ('Invalid Security Answer.', status_code),
    'INVALID_SECURITY_CODE': lambda status_code=401: ('Invalid Security Code.', status_code),

    # User Management
    'USER_NOT_FOUND': lambda status_code=409: ('User not found', status_code),
    'USER_ADD_FAILED': lambda status_code=409: ('User add failed', status_code),
    'USER_ALREADY_EXISTS': lambda status_code=409: ('User already exists', status_code),
    'USER_UPDATE_FAILED': lambda status_code=409: ('User update failed', status_code),
    'USER_DELETE_FAILED': lambda status_code=409: ('User delete failed', status_code),

    # Role Management
    'ROLE_ADD_FAILED': lambda status_code=409: ('Role add failed', status_code),
    'ROLE_ALREADY_EXISTS': lambda status_code=409: ('Role already exists', status_code),
    'ROLE_DELETE_FAILED': lambda status_code=409: ('Role delete failed', status_code),
    'INVALID_ROLE_NAME': lambda status_code=409: ('Role name is not valid', status_code),
    'ROLE_NOT_FOUND': lambda status_code=409: ('Role not found', status_code),
    'ROLE_DELETE_NOT_ALLOWED': lambda status_code=409: ('This role is assigned to other users. You can not delete this role', status_code),
    'ACCESS_PERMISSION_NOT_FOUND': lambda status_code=999: ("User don't have access to the resource. Please contact administrator", status_code),

    # File Management
    'FILE_NOT_FOUND': lambda status_code=404: ('File not found', status_code),
    'FILE_NOT_EXIST': lambda status_code=404: ('File does not exist', status_code),
    'FILE_NOT_ALLOWED': lambda status_code=415: ('Unsupported file type', status_code),
    'FILE_NAME_INVALID': lambda status_code=400: ('Invalid file name', status_code),
    'FILE_WRITE_ERROR': lambda status_code=500: ('Error writing file', status_code),

    # DB Error
    'DB_PERMISSION_DENIED': lambda status_code=403: ('Database permission denied', status_code),
    'DB_WRITE_ERROR': lambda status_code=500: ('Database write failed', status_code),
    'DB_REPLICA_UNAVAILABLE': lambda status_code=503: ('Database replica unavailable', status_code),

    # Common Error
    'NOT_FOUND': lambda status_code=404: ('Requested entity not found', status_code),
    'INVALID_PAGINATION': lambda status_code=400: ('Invalid pagination parameters', status_code),
    'INVALID_DATE_FORMAT': lambda field, status_code=400: ("Invalid date format for {0} please follow YYYY-MM-DD format".format(', '.join(field)), status_code),

}