from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse, marshal_with, marshal
from app import db
from app.university import model as university_model
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
        parser.add_argument('university', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('major', type=str)
        return parser


    def post(self):
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

    def put(self):
        parser = self.put_parser()
        args = parser.parse_args()
        # get user, if no email is provided, a 404 is returned right here
        user_to_update = model.User.query.filter_by(email=args['email']).first()
        if user_to_update:
            for k, v in args:
                user_to_update[k] = v if v else user_to_update[k]
            db.session.commit()
            return make_response(204)
        return make_response("no such user", 404)
        
    def delete(self): pass

class UserList(Resource):
    @marshal_with(model.User.fields)
    def get(self, university):
        parent_uni = university_model.University.query.filter_by(name=university).first()
        if parent_uni:
            return parent_uni.users.all()
        return make_response('no such university', 404)



api.add_resource(SingleUser, '/users/')
api.add_resource(UserList, '/users/<string:university>')