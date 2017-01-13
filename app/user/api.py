from flask import Blueprint, make_response, jsonify
from flask_restful import Api, Resource, reqparse, marshal_with, marshal
from app import db
from app.university import model as university_model
from app.validation import auth
import model
from app.validation import email as validator
from sqlalchemy.exc import IntegrityError
import app.validation.auth

user_blueprint = Blueprint('user', __name__)
api = Api(user_blueprint)


class SingleUser(Resource):
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='you have to provide a username for this user')
        parser.add_argument('email', type=validator.email, required=True, help='you have to provide a valid email for this user')
        parser.add_argument('university_id', type=int, required=True, help='you have to provide a university id for this user')
        parser.add_argument('password', type=str, default=None, required=True, help="you have to provide a password for this user")
        parser.add_argument('major', type=str, default=None)
        return parser

    def put_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=validator.email)
        parser.add_argument('university_id', type=int)
        parser.add_argument('password', type=str)
        parser.add_argument('major', type=str)
        return parser

    def post(self): # works
        """
        @apiVersion 0.1.0
        @api {post} /users/ Create a new user
        @apiName CreateUser
        @apiGroup Users
        @apiDescription Create a new user. Note that you have to provide a unique email and a unique username.
        @apiParam {String} username Unique nickname/username for the new user.
        @apiParam {String} email The users unique email.
        @apiParam {Number} university_id The university the user is enrolled in. The university must be present in the db.
        @apiParam {String} password The users password.
        @apiParam {String} major The subject the new user is majoring in.
        @apiUse UserAlreadyExistsError
        @apiUSe NoSuchResourceError
        @apiUse BadRequest
        @apiUse SuccessfullyCreated
        @apiUse CouldNotBeSavedError
        """
        parser = self.post_parser()
        args = parser.parse_args()
        parent_uni = university_model.University.query.get(args['university_id'])
        if parent_uni:
            new_user = model.User(username=args['username'], email=args['email'], major=args['major'])
            new_user.hash_password(args['password'])
            new_user.owner = parent_uni
            try:
                db.session.add(new_user)
                db.session.commit()
                return make_response('created user', 201)
            except IntegrityError as error:
                s = ""
                if "Duplicate entry" in error.message:
                    s = "this user already exists"
                    return make_response(s, 404)
                else:
                    s = "an error occured, the user could not be saved"
                    return make_response(s, 500)
        return make_response('no such university', 404)

    @auth.token_required
    def get(self, **kwargs):
        """
        @apiVersion 0.1.0
        @api {post} /users/ Get user info
        @apiName GetUser
        @apiGroup Users
        @apiUse TokenRequired
        @apiUse BadRequest
        @apiSuccess {String} username The users name
        @apiSuccess {String} major  The subject the user is majoring in
        @apiSuccess {String} email The users email.
        @apiSuccess {json} The universities the user studies at. See example for the json
        @apiSuccessExample UserInfo:
         HTTP/1.1 200 OK
            {
            "username": "Romue404",
             "university":
                {"city": null, "country": "Germany", "id": 1, "name": "LMU"},
              "major": "Informatik",
              "email": "robert.mueller1990@googlemail.com"
            }
        """
        user = kwargs.get('user')
        user_info = model.User.query.get(user['user_id'])
        return marshal(user_info, model.User.fields['with_university'])

    @auth.token_required
    def put(self, **kwargs): # works
        """
        @apiVersion 0.1.0
        @api {post} /users/ Modify a user
        @apiName ModifyUser
        @apiGroup Users
        @apiUse TokenRequired
        @apiDescription Modify a users information. You may receive an error when trying to set new informations that another user already has, like email.
        @apiParam {String} [email] The users unique email.
        @apiParam {Number} [university_id] The university the user is enrolled in. The university must be present in the db.
        @apiParam {String} [password] The users password.
        @apiParam {String} [major] The subject the new user is majoring in.
        @apiUse BadRequest
        @apiUse NoSuchUserError
        @apiUse SuccessfullyCreated
        """
        user = kwargs.get('user')
        updated = []
        parser = self.put_parser()
        args = parser.parse_args()
        user_to_update = model.User.query.get(user['user_id'])
        if user_to_update:
            for key, value in args.iteritems():
                # last part is to fix requests that have a key but null as a value for that key
                #setattr(user_to_update(user_to_update, k, v if v else getattr(user_to_update,k)))
                if value: # check if uni exists
                    # check for uniqueness violations
                    setattr(user_to_update, key, value)
                    updated.append(key)
        if len(updated) > 0:
            db.session.commit()
            return make_response('updated {properties}.'.format(properties=', '.join(map(str,updated))), 201)
        else:
            return make_response("no such user", 404)

    @auth.token_required
    def delete(self, **kwargs):
        """
        @apiVersion 0.1.0
        @api {delete} /users/ Delete a user
        @apiName DeleteUser
        @apiGroup Users
        @apiUse TokenRequired
        @apiDescription Delete a users. Implementation is NOT done. There may be errors because auf unimplemented cascading behavior.
        @apiParam {Number} id The users unique id.
        @apiUse BadRequest
        @apiUse NoSuchUserError
        @apiUse SuccessfullyDeleted
        """
        user = kwargs.get('user')
        # try to delete if exists
        user_to_delete = model.User.query.get(user['user_id'])
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            return make_response('user deleted', 200)
        return make_response('no such user', 404)


api.add_resource(SingleUser, '/users/')


