from flask_restful import fields
from passlib.apps import custom_app_context as pwd_context
from app.university import model as university_model
from app import db

"""================= many to many realtionships==================="""
GroupMembership = db.Table('groupmembership',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
)


favorite_notes = db.Table('favorite_notes',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)
"""================= many to many realtionships==================="""


class User(db.Model):
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
    profile_img_path = db.Column(db.String(256))
    # if the user is deleted, so are the notes
    notes = db.relationship('Note', backref='creator', lazy='dynamic')
    university = db.relationship('University', foreign_keys='User.university_id')
    # groups can be accessed via many-to-many relationship maybe revert to joined
    groups = db.relationship('Group', secondary=GroupMembership, backref=db.backref('members', lazy='joined'),
                             passive_deletes=False, order_by='desc(Group.id)')
    favorite_notes = db.relationship('Note', secondary=favorite_notes, backref=db.backref('favorited_by', lazy='dynamic'), lazy='dynamic', passive_deletes=False)

    fields = {
        'basic': {
            'email': fields.String,
            'username': fields.String,
            'major': fields.String
        },
        'only_username': {
            'username': fields.String
        },
        'with_university': {
            'email': fields.String,
            'username': fields.String,
            'major': fields.String,
            'university': fields.Nested(university_model.University.fields['basic'])
        },
        'extended': {
            'email': fields.String,
            'username': fields.String,
            'major': fields.String,
            'university': fields.Nested(university_model.University.fields['basic']),
            'groups_count': fields.Integer(attribute=lambda u: len(u.groups)),
            'notes_count': fields.Integer(attribute=lambda u: u.notes.count()),
            'favorite_notes_count': fields.Integer(attribute=lambda u: u.favorite_notes.count())
        }
    }

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, entered_password):
        return pwd_context.verify(entered_password, self.password_hash)

    def is_member_of(self, group):
        return True if group in self.groups else False

    def add_favorite(self, note):
        if not self.is_favorite(note):
            self.favorite_notes.append(note)
            return self

    def remove_favorite(self, note):
        if self.is_favorite(note):
            self.favorite_notes.remove(note)
            return self

    def is_favorite(self, note):
        return self.favorite_notes.filter(favorite_notes.c.note_id == note.id).count() > 0


