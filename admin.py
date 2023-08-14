from models import Admin
from security import Security
from errors import Err, LogLevel, log


class AdminLookup:
    @staticmethod
    def match_key(key):
        """
        Checks if the key matches the admin key and returns True if it does,
        False otherwise.

        :param key: The `key` parameter is the admin key provided on db initisiation that is being compared to db encrypted key
        :return: The function `match_key` returns a boolean value. If the `admin_key` does not match the
        provided `key`, it returns `False`. Otherwise, it returns `True`.
        """
        admin_row = Admin.query.first()
        admin_key = Security.fernet_uuid_decrypt(admin_row.id)
        log("Admin key match requested", LogLevel.INFO)
        if admin_key != key:
            Err.client_return("Invalid Admin Key", LogLevel.ERROR)
            return False
        return True
