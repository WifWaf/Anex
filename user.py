from models import db
from models import User, Data
from datetime import datetime, timedelta
import math
from werkzeug.security import check_password_hash
from errors import Err, LogLevel

LAST_LOGIN_RESET_PERIOD = 10  # minutes


class UserLookup:
    @staticmethod
    def id(id):
        """
        Takes a user id as input, queries the database for a user with that id, and returns a tuple
        indicating whether the user exists and the username if it does.

        :param id: The parameter "id" is the identifier of a user. It is used to query the database and find
        the user with the corresponding id
        :return: a tuple with two values. The first value is a boolean indicating whether the user with the
        given id exists or not. The second value is the username of the user if it exists, or None if the
        user does not exist.
        """
        user = User.query.filter_by(id=id).first().username
        if user is not None:
            return True, user
        return False, None

    @staticmethod
    def username(username):
        """
        Checks if a user with a given username exists in the database and returns a boolean
        value indicating the result along with the user object.

        :param username: The parameter `username` is the username that we want to search for in the database
        :return: a tuple. The first element of the tuple is a boolean value indicating whether the user with
        the given username exists or not. The second element of the tuple is the user object if it exists,
        or None if it doesn't exist.
        """
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return True, user
        return False, None

    @staticmethod
    def email(email):
        """
        Checks if a user with a given email exists in the database and returns a boolean value
        indicating the result along with the user object.

        :param email: The `email` parameter is the email address that is being passed to the `email`
        function. It is used to query the database and find a user with the matching email address
        :return: a tuple. The first element of the tuple is a boolean value indicating whether a user with
        the given email exists or not. The second element is the user object if it exists, or None if it
        doesn't.
        """
        user = User.query.filter_by(email=email).first()
        if user is not None:
            return True, user
        return False, None


class UserManage:
    @staticmethod
    def create(uuid, name, email, password, state, license_key):
        """
        Creates a new user in a database with the provided information.

        :param uuid: A unique identifier for the user
        :param name: The name parameter is the username of the user that you want to create
        :param email: The email parameter is the email address of the user that is being created
        :param password: The "password" parameter is the password that the user wants to set for their
        account
        :param state: The "state" parameter refers to the state of the user. It could be a string
        representing the user's current state, such as "active", "inactive", "pending", etc
        :param license_key: The `license_key` parameter is a unique key or code that is associated with a
        user's license or subscription. It is used to verify the user's eligibility for user data decryption and
        access.
        :return: the value 1.
        """
        try:
            user = User(
                id=str(uuid),
                license=license_key,
                username=name,
                password=password,
                login_attempts=0,
                email=email,
                status=state,
            )
            db.session.add(user)

        except Exception as e:
            return Err.database_return(e)

        db.session.commit()
        return 1


class UserEntity:
    def __init__(self, id):
        """
        Initialises a user object with data retrieved from a database query.

        :param id: The `id` parameter is the unique identifier (user id) of the user. It is used to query the database
        and retrieve the user's information
        """
        user_row = User.query.filter_by(id=id).first()

        if user_row is None:
            Err.client_return(Err.ERROR_MESSAGES['USER_ID_NOT_FOUND'], LogLevel.ERROR)

        self.__set_manage_last_login(user_row)

        self.id = user_row.id
        self.license = user_row.license
        self.password = user_row.password
        self.username = user_row.username
        self.timeout_stamp = user_row.login_timeout
        self.login_attempts = user_row.login_attempts
        self.last_login_attempt = user_row.last_login_attempt
        self.email = user_row.email
        self.status = user_row.status

    @property
    def data(self):
        """
        Returns the most recent data entry for a specific user.
        :return: The code is returning the most recent data entry for a specific user, based on their user
        ID.
        """
        return Data.query.filter_by(user_id=self.id).order_by(Data.created.desc()).first()

    @data.setter
    def data(self, bulk_data):
        """
        Saves bulk data for a user, deletes older entries if there are more than one,
        and prints the count of data entries for the user.

        :param bulk_data: The parameter `bulk_data` is a variable that represents a large amount of data
        that needs to be stored in the database
        """
        try:
            data = Data(
                user_id=str(self.id),
                userData=bulk_data,
            )
            db.session.add(data)

        except Exception as e:
             Err.database_return(e)

        # Delete older entries, as files can be large
        if Data.query.filter_by(user_id=self.id).count() > 1:
            previous_save = Data.query.filter_by(user_id=self.id).order_by(Data.created.desc()).first()
            old_data = Data.query.filter_by(user_id=self.id).filter(Data.id != previous_save.id).all()

            for data in old_data:
                db.session.delete(data)

        db.session.commit()

    def __set_manage_last_login(self, user_row):
        """
        Sets the last login attempt time and manages the login attempts for a user.

        :param user_row: The `user_row` parameter is an object that represents a user in the database. It
        likely contains information such as the user's login attempts, last login attempt time, and other
        relevant data
        """
        last_login_elapse = 255

        if user_row.last_login_attempt is not None:
            last_login_elapse = datetime.now() - user_row.last_login_attempt
            last_login_elapse = math.ceil(last_login_elapse.total_seconds() / 60)

        if last_login_elapse > LAST_LOGIN_RESET_PERIOD:
            user_row.login_attempts = 0

        user_row.last_login_attempt = datetime.now()
        db.session.commit()

    def update(self):
        """
        Updates the attributes of the user object with the corresponding values from
        the database, and the `match_password` function checks if the provided password matches the hashed
        password stored in the user object.
        """
        user_row = User.query.filter_by(username=self.username).first()

        if user_row is None:
            Err.client_return(Err.ERROR_MESSAGES['INVALID_USERNAME_PASSWORD'], LogLevel.INFO)

        self.__set_manage_last_login(user_row)

        self.id = user_row.id
        self.license = user_row.license
        self.password = user_row.password
        self.username = user_row.username
        self.timeout_stamp = user_row.login_timeout
        self.login_attempts = user_row.login_attempts
        self.last_login_attempt = user_row.last_login_attempt
        self.email = user_row.email
        self.status = user_row.status

    def match_password(self, password):
        """
        Checks if a given password matches the hashed password stored in the
        object.

        :param password: The `password` parameter is the password that you want to check against the stored
        password
        :return: the result of the check_password_hash function, which is a boolean value indicating whether
        the provided password matches the hashed password stored in the object.
        """
        return check_password_hash(self.password, password)

    @property
    def login_timeout(self):
        """
        Calculates the time difference between the current time and a timeout stamp, and
        returns the time difference in minutes rounded up to the nearest whole number.
        :return: the number of minutes remaining until the login timeout expires.
        """
        time_difference = self.timeout_stamp - datetime.now()
        return math.ceil(time_difference.total_seconds() / 60)

    @login_timeout.setter
    def login_timeout(self, mins):
        """
        Sets the login timeout for a given number of minutes.

        :param mins: The `mins` parameter is the number of minutes that will be added to the current time to
        set the login timeout
        """
        self.timeout_stamp = datetime.now() + timedelta(minutes=mins)

    def commit(self):
        """
        Updates the user's login attempts, timeout stamp, email, status, and username
        in the database.
        """
        user = User.query.filter_by(id=self.id).first()

        user.login_attempts = self.login_attempts
        user.login_timeout = self.timeout_stamp
        user.email = self.email
        user.status = self.status
        user.username = self.username

        db.session.commit()

