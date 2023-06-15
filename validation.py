import re
import definitions
from models import User, Data, Device, Session
from models import db
from errors import Err
from werkzeug.security import generate_password_hash, check_password_hash


class Validate:

    @staticmethod
    def email(email):
        # Check that the email contains common characters, an '@', and a '.' symbol
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.match(regex, str(email)) is None:
            Err.client_return(Err.ERROR_MESSAGES['EMAIL_STRING'])

        if db.session.query(User.email).filter_by(email=email).scalar() is not None:
            Err.client_return(Err.ERROR_MESSAGES['EMAIL_NOT_UNIQUE'])

    @staticmethod
    def username(username):
        # At last 3 characters long and only letters and numbers
        regex = r'^[A-Za-z0-9]{3,}$'
        if re.match(regex, str(username)) is None:
            Err.client_return(Err.ERROR_MESSAGES['USERNAME_STRING'])

    @staticmethod
    def username_exists(username):
        user = db.session.query(User).filter_by(username=username).first()
        if user is not None:
            return True, user
        return False, None

    @staticmethod
    def password(password):
        regex = r'^[A-Za-z0-9]{5,}$'
        if re.match(regex, str(password)) is None:
            Err.client_return(Err.ERROR_MESSAGES['USERNAME_STRING'])

    @staticmethod
    def password_exist(username, password):
        user = db.session.query(User.username, User.password).filter_by(username=username).first()
        if user is not None:
            if check_password_hash(user.password, password):
                return True, user
        return False, None

    @staticmethod
    def uuid_form(uuid):
        # Use a regular expression to check if the UUID string is in the correct format
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

        if not re.match(pattern, str(uuid)) or uuid is None:
            return False
        return True

    @staticmethod
    def session_key(key):
        if not Validate.uuid_form(key):
            Err.client_return(Err.ERROR_MESSAGES['UUID_FORM'])

        user_row = Session.query.get(str(key))

        if user_row is None:
            Err.client_return(Err.ERROR_MESSAGES['USER_ID_NOT_FOUND'])

        return user_row

    @staticmethod
    def device_id(uuid):
        if not Validate.uuid_form(uuid):
            Err.client_return(Err.ERROR_MESSAGES['DEVICE_UUID_FORM'])

        dev_row = Device.query.get(uuid)

        if dev_row is None:
            Err.client_return(Err.ERROR_MESSAGES['DEVICE_ID'])

        return dev_row.status


    @staticmethod
    def user_key(key):
        if not Validate.uuid_form(key):
            Err.client_return(Err.ERROR_MESSAGES['USER_UUID'])

        user_row = User.query.get(key)

        if user_row is None:
            Err.client_return(Err.ERROR_MESSAGES['USER_ID_NOT_FOUND'])

        return user_row.status
