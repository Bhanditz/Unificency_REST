from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse, marshal_with, marshal
from app import db
from app.university import model as university_model
from app.group import model as group_model
import model
from app.validation import email as validator
from sqlalchemy.exc import IntegrityError

user_blueprint = Blueprint('user', __name__)
api = Api(user_blueprint)


class SingleUser(Resource):
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='you have to provide a username for this user')
        parser.add_argument('email', type=validator.email, required=True, help='you have to provide a valid email for this user')
        parser.add_argument('university', type=str, required=True, help='you have to provide a university for this user')
        parser.add_argument('password', type=str, default=None)
        parser.add_argument('major', type=str, default=None)
        return parser

    def put_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=validator.email, required=True, help='you have to provide a valid email for this user')
        parser.add_argument('id', type=int, required=True,help='you have to provide an id for this user')
        parser.add_argument('university', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('major', type=str)
        return parser

    def delete_parser(self):
        parser = reqparse.RequestParser()
        # authorization has to be added
        parser.add_argument('id', type=db.Integer, required=True, help='you have to provide an id for this user')
        return parser


    def post(self): # works
        parser = self.post_parser()
        args = parser.parse_args()
        parent_uni = university_model.University.query.filter_by(name=args['university']).first()
        if parent_uni:
            new_user = model.User(username=args['username'], email=args['email'], major=args['major'])
            new_user.owner = parent_uni
            try:
                db.session.add(new_user)
                db.session.commit()
                return make_response('user was created', 201)
            except IntegrityError as error:
                s = ""
                if "Duplicate entry" in error.message:
                    s = "this user already exists"
                    return make_response(s, 404)
                else:
                    s = "an error occured, the user could not be saved"
                    return make_response(s, 500)
        return make_response('no such university', 404)

    def put(self): # works
        test = ""
        parser = self.put_parser()
        args = parser.parse_args()
        # get user, if no email is provided, a 404 is returned right here
        user_to_update = model.User.query.get(args['id'])
        if user_to_update:
            for key, value in args.iteritems():
                # last part is to fix requests that have a key but null as a value for that key
                #setattr(user_to_update(user_to_update, k, v if v else getattr(user_to_update,k)))
                if value: # check if uni exists
                    setattr(user_to_update, key, value)
            db.session.commit()
            return make_response('updated major' + test, 200)
        return make_response("no such user", 404)

    def delete(self):
        parser = self.delete_parser()
        args = parser.parse_args()
        # try to delete if exists
        user_to_delete = model.User.query.get(id)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            return make_response('user deleted', 200)
        return make_response('no such user', 404)


class UserList(Resource):
    def get(self, group_id):
        group = group_model.Group.query.get(group_id)
        if group:
            # check if this functions with or without all
            return marshal(group.members.all(), model.User.fields['basic'])
        return make_response('no such university', 404)


api.add_resource(SingleUser, '/users/')
api.add_resource(UserList, '/users/<int:group_id>')