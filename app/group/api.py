from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse, marshal_with
from sqlalchemy.exc import IntegrityError
from flask_restful import marshal
from flask import jsonify
from app import db
import model
from app.validation import email as validator
from app.university import model as university_model

group_blueprint = Blueprint('group', __name__)
api = Api(group_blueprint)


class JoinGroup(Resource):
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=validator.email, required=True, help='you have to provide the users email')
        parser.add_argument('group', type=str, required=True, help='you have to provide a group')
        parser.add_argument('password', type=str, default=None)
        parser.add_argument('major', type=str, default=None)
        return parser
    pass


class GroupsAtUniversity(Resource):
    @marshal_with(model.Group.fields['with_members'])
    def get(self, university):
        groups_at_uni = university_model.University.query.filter_by(name=university).first().groups
        # members has 'joined' property so no need to load them separately into memory
        return groups_at_uni if groups_at_uni else make_response('no such group', 404)


class SingleGroup(Resource):
    @marshal_with(model.Group.fields['basic'])
    def get(self, name):
        group = model.Group.query.filter_by(name=name).first()
        return group if group else make_response('no such group', 404)
    pass

# !!! when returning a user list via group marshaller you have to explicitly load the relationship if dynamic='lazy' !!!
# !!! like so ... group.users ... another possiblity is to do lazy='joined' on the user object
api.add_resource(JoinGroup, '/groups/')
api.add_resource(GroupsAtUniversity, '/groups/<string:university>')
api.add_resource(SingleGroup, '/groups/name/<string:name>')