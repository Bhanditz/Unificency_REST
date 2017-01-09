from app import db
from flask_restful import fields


class Note(db.Model):
    def __init__(self, name, topic, content):
        self.name, self.topic, self.content = name, topic, content

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), nullable=False)
    topic = db.Column('topic', db.String(20), nullable=False)
    name = db.Column('name', db.String(20), nullable=False)
    content = db.Column('content', db.String(999), nullable=False)
    # GROUP - public = db.Column('public')
    # owner (user)

    fields = {
        'name': fields.String,
        'topic': fields.String,
        'content': fields.String
    }
