from flask import abort


class Err:
    ERROR_MESSAGES = {
        'ADMIN_ID': 'Admin ID not recognised',
        'DEVICE_ID': 'Device ID not recognised',
        'DEVICE_UUID_FORM': 'Device form is invalid',
        'KEY_STATUS': 'Key status is not permitted for this request',
        'UUID_FORM': 'UUID form is invalid',
        'JSON_KEY_MISSING': 'Essential json key(s) not found',
        'ASSOCIATED_USER': 'Key Association Mismatch',
        'USERNAME_STRING': 'Username must be at least 3 characters long and contain only standard characters',
        'USER_UUID': 'User UUID form is invalid',
        'MISSING_JSON_DATA': 'Missing JSON File',
        'JSON_DATA_TYPE': 'Json contains invalid datatype',
        'SENSOR_ID_NOT_FOUND': 'Sensor ID not recognised',
        'EMAIL_STRING': 'Email does not have a recognised form',
        'EMAIL_NOT_UNIQUE': 'Email already registered',
        'USERNAME_NOT_UNIQUE': 'Username is already taken',
        'VAR_IS_NONE': ' Value is absent or None',
        'USER_ID_NOT_FOUND': 'User ID not found',
        'USER_STATUS': 'User account not permitted for this request',
        'JSON_FILE_MISSING': 'Unable to retrieve json file',
        'SES_KEY_NOT_FOUND': 'Session key not found',
    }

    # Generic client return function which accepts an optional argument for the ERROR_MESSAGE array
    @staticmethod
    def client_return(text):
        # if the optional var is provided, use it
        print(text)
        if text:
            abort(400, text)
        else:
            abort(400)

    # Generic database return function
    @staticmethod
    def database_return():
        return abort(500)
