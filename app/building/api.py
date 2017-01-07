from flask import Blueprint, jsonify, make_response, abort
from flask_restful import Api, Resource, marshal_with, reqparse
from sqlalchemy.exc import IntegrityError
from app import db
import model


building_blueprint = Blueprint('building', __name__)
api = Api(building_blueprint)


class Buildings(Resource):
    # how the post request for this route looks like
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('country', type=str)
        parser.add_argument('city', type=str, required=True, help='you have to provide a city')
        parser.add_argument('university', type=str, required=True, help='you have to provide a university')
        parser.add_argument('address', type=str, required=True, help='you have to provide an address')
        parser.add_argument('name', type=str)
        parser.add_argument('description', type=str)
        return parser

    def post(self):
        # retrieve post data
        # returns 404 if not valid
        parser = self.post_parser()
        args = parser.parse_args()
        new_building = model.Building(city=args['city'],
                                      university=args['university'],
                                      address=args['address'].strip(),
                                      country=args['country'],
                                      name=args['name'],
                                      description=['description'])
        # save to db
        try:
            db.session.add(new_building)
            db.session.commit()
            # return json
            return make_response('building was added to the database', 201)
        except IntegrityError as error:
            s = ""
            if "Duplicate entry" in error.message:
                s = "a building for this address already exists"
                return make_response(s, 404)
            else:
                s = "an error occured, the building could not be saved"
                return make_response(s, 500)


class BuildingsFromUniversity(Resource):

    @marshal_with(model.Building.fields)
    def get(self, university):
        # client may check if empty
        all_buildings_uni = model.Building.query.filter_by(university=university).all()
        return all_buildings_uni

api.add_resource(Buildings, '/buildings/')
api.add_resource(BuildingsFromUniversity, '/buildings/<string:university>')
