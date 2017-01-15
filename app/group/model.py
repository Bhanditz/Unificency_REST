from app import db
from flask_restful import fields
from app.user import model as user_model
from passlib.apps import custom_app_context as pwd_context


class Group(db.Model):
    __tablename__ = 'groups'

    def __init__(self, name, description, topic_area):
        self.name, self.description, self.topic_area = name, description, topic_area

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column('university_id', db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column('name', db.String(40), nullable=False, unique=True)
    topic_area = db.Column('topic_area', db.String(20), nullable=False)
    password_hash = db.Column('password', db.String(256), default=None)
    description = db.Column('description', db.String(140))
    # backref users
    notes = db.relationship('Note', backref='group', lazy='dynamic')

    fields = {
        'with_members': {
            'id': fields.Integer,
            'name': fields.String,
            'topic_area': fields.String,
            'description': fields.String,
            'members': fields.Nested(user_model.User.fields['only_username'])
        },
        'basic': {
            'id': fields.Integer,
            'name': fields.String,
            'topic_area': fields.String,
            'description': fields.String
        }
    }

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, entered_password):
        return pwd_context.verify(entered_password, self.password_hash)



