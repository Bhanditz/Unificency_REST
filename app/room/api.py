from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse
from sqlalchemy.exc import IntegrityError
from flask_restful import marshal
from flask import jsonify
from app import db
import model
from app.building import model as building_model

room_blueprint = Blueprint('room', __name__)
api = Api(room_blueprint)


class SingleRoom(Resource):
    # how the post request for this route looks like
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('address', type=str, required=True, help='you have to provide an address for this room')
        parser.add_argument('name', type=str, required=True, help='you have to provide name for this room')
        parser.add_argument('seats', type=int)
        parser.add_argument('warning', type=str)
        return parser

    def post(self):
        parser = self.post_parser()
        args = parser.parse_args()
        # if required args are not present flask returns a 400 here
        parent_building = building_model.Building.query.filter_by(address=args['address']).first()
        # only carry on if a building for that room exists
        if not parent_building:
            return make_response('there is no building at this address in our system', 404)
        # keyword owner established the foreign key relationship
        new_room = model.Room(name=args['name'], seats=args['seats'], warning=args['warning'])
        new_room.owner = parent_building
        try:
            db.session.add(new_room)
            db.session.commit()
            return make_response('added room to the database', 201)
        except IntegrityError as error:
            s = ""
            if "Duplicate entry" in error.message:
                s = "this room already exists"
                return make_response(s, 404)
            else:
                s = "an error occured, the building could not be saved"
                return make_response(s, 500)


class RoomsAtAdress(Resource):
    # change this to id
    def get(self, address):
        bm = building_model.Building
        adjusted_address = address.replace('%20', ' ')
        parent_building = bm.query.filter_by(address=adjusted_address).first()
        if not parent_building:
            return make_response('there is no building at this address in our system', 404)
        # do something with the rooms here ... add needed fields that are not classmembers
        # {address: []}
        response = {parent_building.address: marshal(parent_building.rooms.all(), model.Room.fields)}
        return jsonify(response)


class FreeRoomsAtAddress(Resource):
    def get(self, address): pass


api.add_resource(SingleRoom, '/rooms/')
api.add_resource(RoomsAtAdress, '/rooms/<string:address>')
api.add_resource(FreeRoomsAtAddress, '/rooms/free/<string:address>')