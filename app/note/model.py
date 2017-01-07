from app import db
from flask_restful import fields


class Note(db.Model):
    def __init__(self, name, topic, content):
        self.name, self.topic, self.content = name, topic, content

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column('name', db.String(20), nullable=False)
    name = db.Column('name', db.String(20), nullable=False)
    content = db.Column('name', db.String(999), nullable=False)
    # owner (user)

    fields = {
        'name': fields.String,
        'topic': fields.String,
        'content': fields.String
    }
