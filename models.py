from app import app
from sqlalchemy import DateTime, LargeBinary
from sqlalchemy.sql import func
import uuid
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy


# create the extension
db = SQLAlchemy()
db.init_app(app)


@dataclass
class Device(db.Model):
    id: str
    version: str
    desc: str
    status: str
    created: DateTime
    updated: DateTime

    id = db.Column('dev_id', db.String, primary_key=True, nullable=False)
    version = db.Column(db.String, unique=False, nullable=False)
    desc = db.Column(db.String, unique=False, nullable=True)
    status = db.Column(db.String, unique=False, nullable=False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    updated = db.Column(DateTime(timezone=True), onupdate=func.now())


@dataclass
class User(db.Model):
    id: uuid
    username: str
    password: str
    email: str
    status: str
    created: DateTime
    updated: DateTime

    id = db.Column('user_id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String, unique=True, nullable=True)
    status = db.Column(db.String, unique=False, nullable=False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    updated = db.Column(DateTime(timezone=True), onupdate=func.now())


@dataclass
class Session(db.Model):
    id: uuid
    user_id: uuid
    status: str
    created: DateTime
    updated: DateTime
    can_expire: bool
    expires: DateTime

    id = db.Column('ses_key', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    user_id = db.Column(db.Text(length=36), db.ForeignKey('user.user_id'), unique=False)
    status = db.Column(db.String, unique=False, nullable=False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    updated = db.Column(DateTime(timezone=True), onupdate=func.now())
    expires = db.Column(DateTime(timezone=True))
    can_expire = db.Column(db.Boolean, nullable=False)

    user = db.relationship('User', backref=db.backref('ses_user', lazy=True))


@dataclass
class Data(db.Model):
    id: int
    pad_data: str
    mesh_colors: str
    save_date: str
    user_id: uuid
    created: DateTime
    updated: DateTime

    id = db.Column('data_id', db.Integer, primary_key=True, autoincrement=True)
    save_date = db.Column(db.String, unique=False, nullable=True)
    pad_data = db.Column(db.String, unique=False, nullable=True)
    mesh_colors = db.Column(db.String, unique=False, nullable=True)
    user_id = db.Column(db.Text(length=36), db.ForeignKey('user.user_id'), unique=False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    updated = db.Column(DateTime(timezone=True), onupdate=func.now())

    user = db.relationship('User', backref=db.backref('user_id', lazy=True))

    __table_args__ = (
        db.Index('idx_user', 'user_id'),
    )


if __name__ == "__main__":
    with app.app_context():
        print('Creating database...')
        db.create_all()
        print('Finished!')

