from flask import Flask
from waitress import serve
import definitions
from exts import db
import uuid
from security import Security


def create_app():
    """
    Initialises a Flask application, configures a SQLite database, creates
    necessary tables, generates an admin key if it doesn't exist, and registers blueprints for routing.
    :return: The function `create_app` returns an instance of the Flask application.
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///anex.db"
    db.init_app(app)

    with app.app_context():
        print('Initiating server ...')
        from models import Admin
        db.create_all()

        if not Admin.query.first():
            print('No database found. First boot? Creating database and generating admin key ..')
            encrypted_key = Security.fernet_uuid_encrypt(uuid.uuid4())  # Create new admin key
            admin = Admin(
                id=encrypted_key,
                status=definitions.STATUS_ACTIVE,
            )
            db.session.add(admin)
            db.session.commit()
            print('Please keep private and safe! Admin Key:', Security.fernet_uuid_decrypt(admin.id))

        print('Database initialised')
        print('Server has started')

    from views import main as main_blueprint
    app.register_blueprint(main_blueprint)
    Security.Network.init()

    return app


if __name__ == '__main__':
    app = create_app()
    serve(app, host="localhost", port=8000)  # serve app on localhost only
