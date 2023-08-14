import re
from errors import Err, LogLevel


class Validate:
    @staticmethod
    def email(email):
        """
        Checks if an email string is valid by using a regular expression pattern.

        :param email: The parameter `email` is a string that represents an email address
        """
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.match(regex, str(email)) is None:
            Err.client_return(Err.ERROR_MESSAGES['EMAIL_STRING'], LogLevel.INFO)

    @staticmethod
    def username(username):
        """
        Checks if a given username is at least 3 characters long and only contains
        letters and numbers.

        :param username: The parameter `username` is a string that represents the username that needs to be
        validated
        """
        regex = r'^[A-Za-z0-9]{3,}$'
        if re.match(regex, str(username)) is None:
            Err.client_return(Err.ERROR_MESSAGES['USERNAME_STRING'], LogLevel.INFO)

    @staticmethod
    def password(password):
        """
        Checks if a password meets certain criteria and logs an error message if it doesn't.

        :param password: The parameter `password` is a string that represents the password that needs to be
        validated
        """
        regex = r'^[A-Za-z0-9]{5,}$'
        if re.match(regex, str(password)) is None:
            Err.client_return(Err.ERROR_MESSAGES['PASSWORD_STRING'], LogLevel.INFO)

    @staticmethod
    def uuid_form(uuid):
        """
        Checks if a given string is a valid UUID format.

        :param uuid: The `uuid` parameter is a string form of a UUID
        :return: The function `uuid_form` returns `True` if the input `uuid` matches the specified pattern
        and is not `None`, otherwise it returns `False`.
        """
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

        if not re.match(pattern, str(uuid)) or uuid is None:
            return False
        return True
