from flask_login import UserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from flask_restful import fields
from passlib.apps import custom_app_context as pwd_context
from app import db
from instance import config as config
import jwt
import datetime

class User(UserMixin, db.Model):
    """
    Create a User table
    """

    __tablename__ = 'users'

    def __init__(self, username, email, major):
        self.username, self.email, self.major = username, email, major
    # user belongs to a university via !owner!
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column('university_id', db.Integer, db.ForeignKey('universities.id'), nullable=False)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(20), index=True, unique=True)
    major = db.Column(db.String(40))
    password_hash = db.Column(db.String(128))
    # if the user is deleted, so are the notes
    notes = db.relationship('Note', backref='creator', lazy='dynamic', cascade="all, delete-orphan")
    # groups can be accessed via many-to-many relationship
    fields = {
        'basic': {
            'email': fields.String(60),
            'username': fields.String(20),
            'major': fields.String(20)
        },
        'only_username': {
            'username': fields.String(20)
        }
    }

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, entered_password):
        return pwd_context.verify(entered_password, self.password_hash)

