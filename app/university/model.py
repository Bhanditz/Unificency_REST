from app import db
from flask_restful import fields


class University(db.Model):
    __tablename__ = 'universities'
    def __init__(self, name, topic, content):
        self.name, self.topic, self.content = name, topic, content

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(40), nullable=False, unique=True)
    country = db.Column('country', db.String(40))
    city = db.Column('city', db.String(40))
    buildings = db.relationship('Building', backref='owner', lazy='dynamic')
    users = db.relationship('User', backref='owner', lazy='dynamic')
    groups = db.relationship('Group', backref='owner', lazy='dynamic')
    fields = {
        'name': fields.String,
        'country': fields.String,
        'city': fields.String
    }
