from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import fields

from app import db, login_manager


class User(UserMixin, db.Model):
    """
    Create a User table
    """

    __tablename__ = 'users'

    def __init__(self, username, email):
        self.username, self.email = username, email
    # user belongs to a university via !owner!
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column('university_id', db.Integer, db.ForeignKey('universities.id'), nullable=False)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(20), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    notes = db.relationship('Note', backref='owner', lazy='dynamic')

    fields = {
        'email': fields.String(60),
        'username': fields.String(20)
    }

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Employee: {}>'.format(self.username)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


