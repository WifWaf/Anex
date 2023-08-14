from datetime import datetime, timedelta
from models import Session
from models import db
from errors import Err, LogLevel
import definitions
import uuid


class SessionLookup:
    @staticmethod
    def record_by_skey(key):
        """
        Retrieves a record from the Session table based on a given key.

        :param key: The `key` parameter is the value used to search for a record in the database. It is used
        to filter the query by the `id` column. The `id` column is expected to be a string, so the `key`
        parameter should also be a string
        :return: The function `record_by_skey` is returning the first record from the `Session` table that
        matches the given `key`.
        """
        return Session.query.filter_by(id=str(key)).first()

    @staticmethod
    def record_by_user_id(key):
        """
        Retrieves the first session record from the database that matches the given user ID.

        :param key: The `key` parameter is a value that is used to filter the records in the query. In this
        case, it is expected to be a user ID. The function `record_by_user_id` takes this user ID as input
        and returns the first record from the `Session` table where the `
        :return: The function `record_by_user_id` is returning the first record from the `Session` table
        where the `user_id` column matches the provided `key` value.
        """
        return Session.query.filter_by(user_id=str(key)).first()


class SessionManage:
    @staticmethod
    def create(user_id, expiration_minutes=720):
        """
        Creates a session with a unique ID, user ID, expiration time, and adds it to the
        database.

        :param user_id: The `user_id` parameter is the unique identifier of the user for whom the session is
        being created. It is used to associate the session with a specific user in the database
        :param expiration_minutes: The `expiration_minutes` parameter is an optional parameter that
        specifies the number of minutes after which the session will expire. By default, it is set to 720
        minutes (12 hours), defaults to 720 (optional)
        :return: the value of the variable "key".
        """
        key = uuid.uuid4()

        try:
            session = Session(
                id=str(key),
                user_id=user_id,
                status=definitions.STATUS_ACTIVE,
                can_expire=True,
                expires=datetime.now() + timedelta(minutes=expiration_minutes)
            )
            db.session.add(session)

        except Exception as e:
            return Err.database_return(e)

        db.session.commit()
        return key

    @staticmethod
    def delete(user_id):
        """
        Deletes a user from the database based on their user ID.

        :param user_id: The user_id parameter is the unique identifier of the user whose data needs to be
        deleted from the database
        """
        Session.query.filter_by(user_id=user_id).delete()
        db.session.commit()


class SessionEntity:
    def __init__(self, key):
        """
        Initializes an object with attributes based on a session row retrieved from a
        database.

        :param key: The `key` parameter is used to identify a session in the database. It is used to query
        the `Session` table and retrieve the corresponding session row
        """
        ses_row = Session.query.filter_by(id=str(key)).first()

        if ses_row is None:
            Err.client_return(Err.ERROR_MESSAGES['INVALID_SESSION'], LogLevel.WARNING)

        self.id = ses_row.id
        self.user_id = ses_row.user_id
        self.status = ses_row.status
        self.created = ses_row.created
        self.updated = ses_row.updated
        self.can_expire = ses_row.can_expire
        self.expires = ses_row.expires

    def update(self, key):
        """
        Updates the attributes of an object based on the values retrieved from a database query.

        :param key: The `key` parameter is used to identify a specific session in the database. It is used
        to query the `Session` table and retrieve the corresponding session row
        """
        ses_row = Session.query.filter_by(id=str(key)).first()

        if ses_row is None:
            Err.client_return(Err.ERROR_MESSAGES['INVALID_SESSION'], LogLevel.WARNING)

        self.id = ses_row.id
        self.user_id = ses_row.user_id
        self.status = ses_row.status
        self.created = ses_row.created
        self.updated = ses_row.updated
        self.can_expire = ses_row.can_expire
        self.expires = ses_row.expires

    def commit(self):
        """
        Retrieves session data from the database and updates the current session object
        with the retrieved data before committing the changes to the database.
        """
        ses_row = Session.query.filter_by(id=str(self.id)).first()

        if ses_row is None:
            Err.client_return(Err.ERROR_MESSAGES['INVALID_SESSION'], LogLevel.WARNING)

        self.id = ses_row.id
        self.user_id = ses_row.user_id
        self.status = ses_row.status
        self.created = ses_row.created
        self.updated = ses_row.updated
        self.can_expire = ses_row.can_expire
        self.expires = ses_row.expires

        db.session.commit()

    def delete(self):
        """
        Deletes a record from the database based on its ID.
        """
        Session.query.filter_by(id=self.id).delete()
        db.session.commit()

    def expired(self):
        """
        Checks if an object has expired and updates its status if necessary.
        :return: a boolean value. It returns True if the item has expired and its status has been set to
        "inactive", and False otherwise.
        """
        if self.can_expire is True:
            if datetime.now() > self.expires:
                if self.status != definitions.STATUS_INACTIVE:
                    self.status = definitions.STATUS_INACTIVE
                    self.commit()
                return True
        return False
