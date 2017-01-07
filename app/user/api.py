from flask import Blueprint
from flask_restful import Api, Resource
from app import db

user_blueprint = Blueprint('user', __name__)
api = Api(user_blueprint)


class SingleUser(Resource):
    pass
class UserList(Resource):
    pass

api.add_resource(SingleUser, '/users/<int:id>')
api.add_resource(UserList, '/users/')