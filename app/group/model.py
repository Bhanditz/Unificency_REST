from app import db
from flask_restful import fields
from app.user import model as user_model

# many to many
GroupMembership = db.Table('groupmembership',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)


class Group(db.Model):
    __tablename__ = 'groups'

    def __init__(self, name, description, topic_area, password=None):
        self.name, self.description, self.password, self.topic_area = name, description, password, topic_area

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column('university_id', db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column('name', db.String(40), nullable=False, unique=True)
    topic_area = db.Column('topic_area', db.String(20), nullable=False)
    password = db.Column('password', db.String(256))
    description = db.Column('description', db.String(140))
    members = db.relationship('User', secondary=GroupMembership, backref=db.backref('groups', lazy='joined'))
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



