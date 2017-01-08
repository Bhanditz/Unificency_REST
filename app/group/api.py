from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse
from sqlalchemy.exc import IntegrityError
from flask_restful import marshal
from flask import jsonify
from app import db
import model
from app.building import model as building_model

room_blueprint = Blueprint('group', __name__)
api = Api(room_blueprint)


class JoinGroup(Resource):
    pass


class GroupsAtUniversity(Resource):
    pass


class SingleGroup(Resource):
    def get(self, name):
        pass
    pass


api.add_resource(JoinGroup, '/groups/')
api.add_resource(SingleGroup, '/groups/<string:name>')