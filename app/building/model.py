from app import db
from flask_restful import fields, reqparse


class Building(db.Model):
    __tablename__ = 'buildings'

    def __init__(self, address, name=None, description=None):
        self.address, self.name, self.description = address, name, description

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    university_id = db.Column('university_id', db.Integer,db.ForeignKey('universities.id'), nullable=False)
    address = db.Column('address', db.String(40), nullable=False)
    name = db.Column('name', db.String(40))
    description = db.Column('description', db.String(80))
    rooms = db.relationship('Room', backref='owner', lazy='dynamic')
    __table_args__ = (db.UniqueConstraint('university_id', 'address', 'name', name='_university_address_name_'),)
    # how we would like our json output to look like
    fields = {
        'address': fields.String,
        'name': fields.String(default=None),
        'description': fields.String(default=None)
    }
