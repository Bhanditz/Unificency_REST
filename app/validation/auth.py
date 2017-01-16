import jwt
import datetime
from datetime import datetime, timedelta
from flask import request, jsonify, make_response, Blueprint
from flask_restful import Api, reqparse, Resource
from app.user import model as user_model
from instance import config
from functools import wraps


SECRET_KEY = config.SECRET_KEY
auth_blueprint = Blueprint('auth', __name__)
api = Api(auth_blueprint)


def generate_auth_token(payload, expiration=30, algorithm='HS256'):
    payload.update({'exp': datetime.utcnow() + timedelta(days=30)})
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm)
    return {'token': jwt_token.decode('utf-8')}


def token_required(f):
    @wraps(f)
    def validate(*args, **kwargs):
        jwt_token = request.headers.get('authorization', None)
        token_data = None
        if not jwt_token:
            return make_response(jsonify({'message': 'You are not authorized to access this resource'}), 401)
        try:
            token_data = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
            kwargs['user'] = token_data
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return make_response(jsonify({'message': 'Token is invalid'}), 400)
        return f(*args, **kwargs)
    return validate


class Auth(Resource):
    def login_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='you have to provide an email to login')
        parser.add_argument('password', type=str, required=True, help='you have to provide a password to login')
        return parser

    def post(self):
        """
        @apiVersion 0.1.0
        @api {put} /login/
        @apiName Login / get Token
        @apiGroup Login
        @apiDescription Login a user and receive a token.
        @apiParam {String} email A topic area which describes the purpose of this group.
        @apiParam {String} password A description for group.
        @apiUse TokenRequired
        @apiUse NoSuchUserError
        @apiUse BadRequest
        @apiSuccess 200 LoginSuccessfull User logged in.
        @apiSuccessExample LoginSuccessfull:
          HTTP/1.1 200 OK
          {
            "token:" "...yourToken..."
            }
        """
        # needs doc
        args = self.login_parser().parse_args()
        user = user_model.User.query.filter_by(email=args['email']).first()
        if not user:
            return make_response(jsonify({'message': 'No such user'}), 404)
        pw_check = user.verify_password(args['password'])
        if not pw_check:
            return make_response(jsonify({'message':'Incorrect password'}, 401))
        token_response_json = generate_auth_token({'user_id': user.id})
        return make_response(jsonify(token_response_json), 200)


api.add_resource(Auth, '/login/')
