from app import db
from flask_restful import fields, reqparse


class Building(db.Model):
    __tablename__ = 'buildings'

    def __init__(self, country, city, university, address, name=None, description=None):
        self.country, self.city, self.university = country, city, university
        self.address, self.name, self.description = address, name, description

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column('country', db.String(40))
    city = db.Column('city', db.String(40), nullable=False)
    university = db.Column('university', db.String(40), nullable=False)
    address = db.Column('address', db.String(40), nullable=False, unique=True)
    name = db.Column('name', db.String(40))
    description = db.Column('description', db.String(80))
    rooms = db.relationship('Room', backref='owner', lazy='dynamic')
    # how we would like our json output to look like
    fields = {
        'country': fields.String(default=None),
        'city': fields.String,
        'university': fields.String,
        'address': fields.String,
        'name': fields.String(default=None),
        'description': fields.String(default=None)
    }
