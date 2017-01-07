from app import db
from daysEnum import Days
from flask_restful import fields
from sqlalchemy.types import Enum


class Room(db.Model):
    __tablename__ = 'rooms'

    def __init__(self, name, seats, warning=None, **kwargs):
        self.name = name
        self.seats = seats
        self.warning = warning

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    building_id = db.Column('building_id', db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    name = db.Column('name', db.String(20), nullable=False)
    seats = db.Column('seats', db.Integer)
    warning = db.Column('warning', db.String(40))
    __table_args__ = (db.UniqueConstraint('building_id', 'name', name='_building_roomname_'),)
    # this is just for programming convenience!
    # Database is not affected since it only needs a relationship via foreign keys
    # RoomFree now has a virtual(!) column named room. room in myRoom.free.all(): pass
    free = db.relationship('RoomFree', backref='owner', lazy='dynamic')
    # how we would like our json output to look like
    fields = {
            'name': fields.String,
            'seats': fields.Integer,
            'warning': fields.String(default=None)
    }


class RoomFree(db.Model):
    __tablename__ = 'roomfree'
    # in order for the json output to work, kwargs will have to provide a building and a room String!
    def __init__(self, room_id, day, from_, to_):
        self.room_id = room_id
        self.day = day
        self.from_ = from_
        self.to_ = to_
    #possible to do the following:  RoomFre(....owner=nameofroom)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column('room_id', db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    day = db.Column('day', Enum(Days), nullable=False)
    from_ = db.Column('from', db.Time, nullable=False)
    to_ = db.Column('to', db.Time, nullable=False)
    # how we would like our json output to look like
    fields = {
        'room': fields.String,
        'day': fields.String,
        'from': fields.String(attribute='from_'),
        'to': fields.String(attribute='to_')
    }



