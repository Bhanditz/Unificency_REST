from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse, marshal_with
from sqlalchemy.exc import IntegrityError
from flask_restful import marshal
from flask import jsonify
from app import db
import model
from app.validation import email as validator
from app.university import model as university_model
from app.user import model as user_model

group_blueprint = Blueprint('group', __name__)
api = Api(group_blueprint)


class JoinGroup(Resource):
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_email', type=validator.email, required=True, help='you have to provide a valid email')
        parser.add_argument('group_password', type=str, default=None)
        return parser

    def put(self, id):
        parser = self.post_parser()
        args = parser.parse_args()
        # password protection check to come
        group_to_join = model.Group.query.get(id)
        user = user_model.User.query.find_by(email=args['user_email']).first()
        if group_to_join and user:
            group_to_join.members.append(user)
            db.session.commit()
            return make_response('user {user} added to group {group}'.format(user=user.username,
                                                                             group=group_to_join.name), 200)
        return make_response('no such user or group', 404)

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
api.add_resource(JoinGroup, '/groups/join/<int:id>')
api.add_resource(GroupsAtUniversity, '/groups/<string:university>')
api.add_resource(SingleGroup, '/groups/name/<string:name>')