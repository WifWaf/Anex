from flask import request
import definitions
import uuid
from validation import Validate
from werkzeug.security import generate_password_hash
from session import SessionEntity, SessionLookup, SessionManage
from user import UserEntity, UserLookup, UserManage
from security import Security
import json
from errors import Err, LogLevel
from flask import Blueprint
from license import LicenseEntity, LicenseManage
from admin import AdminLookup

main = Blueprint('main', __name__)


@main.route('/api/create/user/<int:ikey>', methods=['POST'])
def create_user(ikey):
    """
    Creates a new user with the provided information, validates the data,
    checks for uniqueness of username and email, verifies the license key, and returns a success
    message.

    :param ikey: The parameter `ikey` is as simple access key used provided by the app. It is compared with
    the `access_key` stored in the `Security.Network` class to ensure that the request is coming from a
    valid source
    :return: a dictionary with a "message" key and a value of "User Successfully Created", along with a
    status code of 200.
    """
    if ikey != Security.Network.access_key:
        Err.client_return(Err.ERROR_MESSAGES['INVALID_ORIGIN'], LogLevel.ERROR)

    user_email = request.json.get('email')
    password = request.json.get('password')
    user_name = request.json.get('username')
    license_key = request.json.get('key')

    # validate the characters in data
    Validate.email(user_email)
    Validate.password(password)
    Validate.username(user_name)
    Validate.uuid_form(license_key)

    if UserLookup.username(user_name)[0] is True:
        Err.client_return(Err.ERROR_MESSAGES['USERNAME_NOT_UNIQUE'], LogLevel.INFO)

    if UserLookup.email(user_email)[0] is True:
        Err.client_return(Err.ERROR_MESSAGES['EMAIL_NOT_UNIQUE'], LogLevel.INFO)

    user_license = LicenseEntity(license_key)

    if user_license.expired is True or user_license.claimed is True or user_license.status != definitions.STATUS_ACTIVE:
        Err.client_return(Err.ERROR_MESSAGES['INVALID_LICENSE'], LogLevel.INFO)

    user_license.claimed = True
    user_license.commit()

    hashed_password = generate_password_hash(password)
    gen_user_id = str(uuid.uuid4())
    UserManage.create(gen_user_id, user_name, user_email, hashed_password, definitions.STATUS_ACTIVE, license_key)

    return {"message": "User Successfully Created"}, 200


@main.route('/api/login/<int:ikey>', methods=['POST'])
def login(ikey):
    """
    Handles the login process for a user, including validating the username and
    password, checking the user's account status and license, and creating a session key for the user.

    :param ikey: The parameter `ikey` is as simple access key used provided by the app. It is compared with
    the `access_key` stored in the `Security.Network` class to ensure that the request is coming from a
    valid source
    :return: a dictionary with a key "key" and its corresponding value being the string representation
    of the variable "key". It is also returning the status code 200.
    """
    if ikey != Security.Network.access_key:
        Err.client_return(Err.ERROR_MESSAGES['INVALID_ORIGIN'], LogLevel.ERROR)

    username = request.json.get('username')
    password = request.json.get('password')

    Validate.username(username)
    Validate.password(password)

    user_found, user_record = UserLookup.username(username)
    if user_found is False:
        Err.client_return(Err.ERROR_MESSAGES['INVALID_USERNAME_PASSWORD'], LogLevel.INFO)

    user_rec = UserEntity(user_record.id)

    if user_rec.login_attempts > 4:
        if user_rec.login_timeout <= 0:
            user_rec.login_attempts = 0
            user_rec.commit()
        else:
            Err.client_return(Err.ERROR_MESSAGES['LOGIN_ATTEMPTS'], LogLevel.INFO,
                              f"\nTry again in {user_rec.login_timeout} minutes")

    if Security.User.hash_password_compare(user_rec.password, password) is False:
        user_rec.login_attempts += 1

        if user_rec.login_attempts > 4:
            user_rec.login_timeout = 1

        user_rec.commit()
        Err.client_return(Err.ERROR_MESSAGES['INVALID_USERNAME_PASSWORD'], LogLevel.INFO)

    user_rec.login_attempts = 0       # if login is successful, reset failed login count
    if user_rec.status != definitions.STATUS_ACTIVE:
        Err.client_return(Err.ERROR_MESSAGES['INVALID_ACCOUNT_STATE'], LogLevel.INFO)

    user_license = LicenseEntity(user_rec.license)
    if user_license.expired is True or user_license.claimed is False or user_license.status != definitions.STATUS_ACTIVE:
        Err.client_return(Err.ERROR_MESSAGES['INVALID_LICENSE'], LogLevel.INFO)

    session_row = SessionLookup.record_by_user_id(user_rec.id)
    if session_row is not None:
        SessionManage.delete(user_rec.id)

    key = SessionManage.create(user_rec.id)
    return {"key": str(key)}, 200


@main.route('/api/license/<uuid:admin_key>/<int:duration>', methods=['GET'])
def create_license(admin_key, duration):
    """
    Creates a license using an admin key and a duration.

    :param admin_key: The admin_key parameter is the admin key UUID. It is used to
    validate the admin user and ensure that they have the necessary permissions to create a license
    :param duration: The duration parameter is the length of time for which the license will be valid.
    It is typically specified in days, months, or years
    :return: the result of the `LicenseManage.create()` function, which is creating a new license with a
    randomly generated UUID and the specified duration.
    """
    if not Validate.uuid_form(admin_key):
        Err.client_return(Err.ERROR_MESSAGES['UUID_FORM'], LogLevel.INFO)

    if AdminLookup.match_key(admin_key) is False:
        Err.client_return(Err.ERROR_MESSAGES['ADMIN_ID'], LogLevel.INFO)

    return LicenseManage.create(str(uuid.uuid4()), duration)


@main.route('/api/save_user_data/<uuid:skey>', methods=['POST'])
def save_user_data(skey):
    """
    Saves user data after validating the session key and encrypting the data.

    :param skey: The parameter "skey" is a session key that is used to identify and authenticate the
    user session
    :return: a dictionary with the key "message" and the value "User Authenticated, saving data", along
    with the HTTP status code 200.
    """
    Validate.uuid_form(skey)
    user_session = SessionEntity(skey)
    if user_session.expired() is True:
        Err.client_return(Err.ERROR_MESSAGES['INVALID_SESSION'], LogLevel.WARNING)

    json_dump = json.dumps(request.json)
    user_entity = UserEntity(user_session.user_id)

    user_entity.data = Security.fernet_encrypt(json_dump)
    return {"message": "User Authenticated, saving data"}, 200


@main.route('/api/load_user_data/<uuid:skey>', methods=['GET'])
def load_user_data(skey):
    """
    Loads and decrypts user data based on a session key.

    :param skey: The parameter `skey` is a session key that is used to identify and authenticate a user
    session
    :return: a dictionary with the key "userData" and the decrypted user data as the value. The HTTP
    status code 200 is also being returned.
    """
    Validate.uuid_form(skey)
    user_session = SessionEntity(skey)
    if user_session.expired() is True:
        Err.client_return(Err.ERROR_MESSAGES['INVALID_SESSION'], LogLevel.WARNING)

    user_entity = UserEntity(user_session.user_id)
    user_data_rec = user_entity.data

    if user_data_rec is None:
        return {'message': 'No data found for user'}, 404

    decrypted_data = Security.fernet_decrypt(user_data_rec.userData)

    return {"userData": str(decrypted_data)}, 200
