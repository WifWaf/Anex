from flask import abort
import logging
from enum import Enum

DEFAULT_LOGGING_LEVEL = logging.INFO

logging.basicConfig(
    filename='anex.log',
    format='%(asctime)s %(levelname)s %(message)s',
    level=DEFAULT_LOGGING_LEVEL,
    datefmt='%Y-%m-%d %H:%M:%S')

root_logger = logging.getLogger()
handler = logging.StreamHandler()
root_logger.addHandler(handler)


class LogLevel(Enum):
    ERROR = 0
    WARNING = 1
    DEBUG = 2
    INFO = 3


def log(text, level=LogLevel.ERROR, optional=""):
    if level == LogLevel.ERROR:
        logging.error(text + optional)
    elif level == LogLevel.WARNING:
        logging.warning(text + optional)
    elif level == LogLevel.INFO:
        logging.info(text + optional)
    elif level == LogLevel.DEBUG:
        logging.debug(text + optional)


class Err:
    ERROR_MESSAGES = {
        'ADMIN_ID': 'Admin ID not recognised',
        'REG_KEY_NOT_FOUND': 'Registration Key Not Found',
        'DEVICE_UUID_FORM': 'Device form is invalid',
        'KEY_STATUS': 'Key status is not permitted for this request',
        'UUID_FORM': 'UUID form is invalid',
        'JSON_KEY_MISSING': 'Essential json key(s) not found',
        'ASSOCIATED_USER': 'Key Association Mismatch',
        'USERNAME_STRING': 'Username must be at least 3 characters long and contain only standard characters',
        'PASSWORD_STRING': 'Username must be at least 3 characters long and contain only standard characters',
        'USER_UUID': 'User UUID form is invalid',
        'MISSING_JSON_DATA': 'Missing JSON File',
        'JSON_DATA_TYPE': 'Json contains invalid datatype',
        'EMAIL_STRING': 'Email does not have a recognised form',
        'EMAIL_NOT_UNIQUE': 'Email already registered',
        'USERNAME_NOT_UNIQUE': 'Username already taken',
        'VAR_IS_NONE': ' Value is absent or None',
        'USER_ID_NOT_FOUND': 'User ID not found',
        'USER_STATUS': 'User account not permitted for this request',
        'JSON_FILE_MISSING': 'Unable to retrieve json file',
        'SES_KEY_NOT_FOUND': 'Session key not found',
        'INVALID_ORIGIN': 'Invalid request origin',
        'INVALID_USERNAME_PASSWORD': 'Incorrect Username or Password',
        'INVALID_ACCOUNT_STATE': 'User Account Requires Activation',
        'LOGIN_ATTEMPTS': 'Too Many Login Requests.',
        'INVALID_LICENSE': 'Invalid license key',
        'INVALID_SESSION': 'Invalid session key'

    }

    logging.basicConfig(
        filename='anex.log',
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    @staticmethod
    def disable():
        logging.disable(logging.NOTSET)

    @staticmethod
    def enable():
        logging.disable(DEFAULT_LOGGING_LEVEL)

    @staticmethod
    def client_return(text, level=LogLevel.ERROR, optional=""):
        log("{400} " + text, level, optional)

        if text:
            abort(400, text + optional)
        else:
            abort(400)

    @staticmethod
    def database_return():
        return abort(500)
