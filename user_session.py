from datetime import datetime, timedelta
from models import Session
from models import db
from errors import Err
from validation import Validate
import definitions
import uuid


class UserSession:
    @staticmethod
    def is_valid(session_key):
        session_row = UserSession.get_session(session_key)

        if session_row is None:
            return False

        if session_row.expires and session_row.expiration_time > datetime.now():
            return False

        return True

    @staticmethod
    def create_session(user_id, expiration_minutes=60):
        _user_id = str(user_id)
        account_status = Validate.user_key(_user_id)

        if account_status != definitions.STATUS_ACTIVE:
            Err.client_return(Err.ERROR_MESSAGES['USER_STATUS'], account_status)

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

        # Lazy commit does not seem to be working?
        db.session.commit()
        return key

    @staticmethod
    def get_session(session_key):
        return Session.query.filter_by(session_key=session_key).first()

    @staticmethod
    def delete_session(session_key):
        Session.query.filter_by(session_key=session_key).delete()
        db.session.commit()
