from flask import Blueprint, jsonify, make_response
from flask_restful import Api, Resource, marshal_with, reqparse, marshal
from sqlalchemy.exc import IntegrityError
from app import db
import model
from app.university import model as university_model


building_blueprint = Blueprint('building', __name__)
api = Api(building_blueprint)


class Buildings(Resource):
    # how the post request for this route looks like
    def post_parser(self):
        parser = reqparse.RequestParser()
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

        # save to db
        try:
            um = university_model.University
            parent_uni = um.query.filter_by(name=args['university']).first()
            if parent_uni:
                new_building = model.Building(address=args['address'].strip(),
                                              name=args['name'],
                                              description=['description'])
                new_building.owner = parent_uni
                db.session.add(new_building)
                db.session.commit()
                # return json
                return make_response('building was added to the database', 201)
            return make_response('no such university', 404)
        except IntegrityError as error:
            s = ""
            if "Duplicate entry" in error.message:
                s = "a building for this address already exists"
                return make_response(s, 404)
            else:
                s = "an error occured, the building could not be saved"
                return make_response(s, 500)


class BuildingsFromUniversity(Resource):

    def get(self, university): # works
        parent_uni = university_model.University.query.filter_by(name=university).first()
        if parent_uni:
            all_buildings_uni = parent_uni.buildings.all()
            if all_buildings_uni:
                response = {parent_uni.name: marshal(all_buildings_uni, model.Building.fields)}
                return jsonify(response)
        return make_response('no uni or buildings found', 404)

api.add_resource(Buildings, '/buildings/')
api.add_resource(BuildingsFromUniversity, '/buildings/<string:university>')
