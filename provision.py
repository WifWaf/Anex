import definitions
from models import User, Data, Device
from models import db
from errors import Err
from flask import jsonify


class Provision:
    class Request:
        @staticmethod
        def session_key(userid):
            pass

        @staticmethod
        def user_data(userid):
            latest_data = Data.query.filter_by(user_id=userid).order_by(Data.created.desc()).first()
            if latest_data:
                # Convert the latest data to a JSON response
                response = {
                    'padData': latest_data.pad_data,
                    'meshColor': latest_data.mesh_colors,
                    'saveDate': latest_data.created
                }
                return response
            return None

    class Register:
        @staticmethod
        def device(uuid, ver):
            try:
                device = Device(
                    id=str(uuid),
                    version=ver,
                    status=definitions.STATUS_ACTIVE
                )
                db.session.add(device)

            except Exception as e:
                return Err.database_return(e)

            # Lazy commit does not seem to be working?
            db.session.commit()
            return 1

        @staticmethod
        def user(uuid, name, email, password):
            try:
                user = User(
                    id=str(uuid),
                    username=name,
                    password=password,
                    email=email,
                    status=definitions.STATUS_ACTIVE,
                )
                db.session.add(user)

            except Exception as e:
                return Err.database_return(e)

            # Lazy commit does not seem to be working?
            db.session.commit()
            return 1

        @staticmethod
        def user_data(uuid, pad_data, mesh_colors):
            try:
                data = Data(
                    user_id=str(uuid),
                    pad_data=pad_data,
                    mesh_colors=mesh_colors,
                )
                db.session.add(data)

            except Exception as e:
                return Err.database_return(e)

            # Delete older entries, as files can be large
            if Data.query.filter_by(user_id=uuid).count() > 1:
                previous_save = Data.query.filter_by(user_id=uuid).order_by(Data.created.desc()).first()
                old_data = Data.query.filter_by(user_id=uuid).filter(Data.id != previous_save.id).all()

                for data in old_data:
                    db.session.delete(data)

            print("Data Count for User: " + str(Data.query.filter_by(user_id=uuid).count()))
            # Lazy commit does not seem to be working?
            db.session.commit()
            return 1

