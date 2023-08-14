from sqlalchemy import DateTime
from sqlalchemy.sql import func
import uuid
from dataclasses import dataclass
from exts import db


@dataclass
class User(db.Model):
    id: uuid
    license: uuid
    username: str
    password: str
    login_attempts: int
    login_timeout: DateTime
    last_login_attempt: DateTime
    email: str
    status: str
    created: DateTime
    updated: DateTime

    id = db.Column('user_id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    license = db.Column(db.Text(length=36), db.ForeignKey('license.license_id'), unique=False, nullable=False)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    login_attempts = db.Column(db.Integer, nullable=False)
    login_timeout = db.Column(DateTime(timezone=True), nullable=True)
    last_login_attempt = db.Column(DateTime(timezone=True), nullable=True)
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
    userData: str
    user_id: uuid
    created: DateTime
    updated: DateTime

    id = db.Column('data_id', db.Integer, primary_key=True, autoincrement=True)
    userData = db.Column(db.String, unique=False, nullable=True)
    user_id = db.Column(db.Text(length=36), db.ForeignKey('user.user_id'), unique=False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    updated = db.Column(DateTime(timezone=True), onupdate=func.now())

    user = db.relationship('User', backref=db.backref('user_id', lazy=True))

    __table_args__ = (
        db.Index('idx_user', 'user_id'),
    )


@dataclass
class License(db.Model):
    id: uuid
    status: str
    created: DateTime
    updated: DateTime
    can_expire: bool
    claimed: bool
    expires: DateTime

    id = db.Column('license_id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    status = db.Column(db.String, unique=False, nullable=False)
    expires = db.Column(DateTime(timezone=True), nullable=False)
    can_expire = db.Column(db.Boolean, nullable=False)
    claimed = db.Column(db.Boolean, nullable=False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    updated = db.Column(DateTime(timezone=True), onupdate=func.now())


@dataclass
class Admin(db.Model):
    id: uuid
    status: str
    created: DateTime
    updated: DateTime

    id = db.Column('user_id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    status = db.Column(db.String, unique=False, nullable=False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    updated = db.Column(DateTime(timezone=True), onupdate=func.now())
