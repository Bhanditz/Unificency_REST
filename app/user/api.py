import os
import sys
from flask import Blueprint, make_response, jsonify, request, send_file, send_from_directory
from flask_restful import Api, Resource, reqparse, marshal_with, marshal
from app import db
from app.university import model as university_model
from app.validation import auth
import model
from app.validation import email as validator
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import config
from app.resources import response
from app.group import model as group_model

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
                public_group = group_model.Group.query.filter_by(name='public',university_id=parent_uni.id).first()
                if not public_group:
                    public_group = group_model.Group(name='public',
                                                     description='Diese Notizen sind fuer alle Benutzer sichtbar',
                                                     topic_area='oeffentlich')
                    parent_uni.add_group(public_group)
                    db.session.add(public_group)
                public_group.add_user(new_user)
                db.session.commit()
                return make_response(jsonify({'message': 'created user'}))
            except IntegrityError as error:
                db.session.rollback()
                s = ""
                if "Duplicate entry" in error.message:
                    message = ""
                    if 'email' in error.message:
                        message += 'This email is already in use.'
                    if 'name' in error.message:
                        message += 'This username is already in use.'
                    return make_response(jsonify({'message': message}), 404)
                else:
                    s = "an error occured, the user could not be saved"
                    return make_response(jsonify({'message': s}), 500)
        return make_response(jsonify({'message': 'no such university'}), 404)

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
        @apiSuccess {String} university The universities the user studies at. See example for the json
        @apiSuccess {Integer} groups_count Number of groups the user is enrolled in,
        @apiSuccess {Integer} notes_count Number of notes the user has posted so far
        @apiSuccess {Integer} favorite_notes_count Number of notes the user favors
        @apiSuccessExample UserInfo:
         HTTP/1.1 200 OK
            {
            "username": "Max Mustermann",
             "university":
                {"city": null, "country": "Germany", "id": 1, "name": "LMU"},
              "major": "Informatik",
              "email": "robert.mueller1990@googlemail.com",
              "groups_count": 5,
              "notes_count": 2,
              "favorite_notes_count": 3
            }
        """
        user = kwargs.get('user')
        user_info = model.User.query.get(user['user_id'])
        return marshal(user_info, model.User.fields['extended'])

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
            json_response = {'message': 'updated {properties}.'.format(properties=', '.join(map(str,updated)))}
            return make_response(jsonify(json_response), 201)
        else:
            return make_response(jsonify({'message': 'no such user'}), 404)

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
            return make_response(jsonify({'message':'user deleted'}))
        return make_response(jsonify({'message': 'no such user'}), 404)


class ProfilePic(Resource):
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in config.Config().ALLOWED_EXTENSIONS
    @auth.token_required
    def post(self, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {post} /users/images/ Add a profile pic
        @apiName AddProfilePic
        @apiGroup Users
        @apiUse TokenRequired
        @apiDescription Upload a profile pic.
        @apiUse BadRequest
        @apiUse NoSuchUserError
        """
        if 'file' not in request.files:
            return response.simple('You have to provide a file', 404)
        user_id = kwargs.get('user')['user_id']
        user = model.User.query.get(user_id)
        if not user:
            return response.simple_response('no such user', status=404)
        file = request.files['file']
        if file.filename == '':
            return request.simple('Empty file', 404)
        if not self.allowed_file(file.filename):
            return response.simple_response('this kind of data is not allowed', 400)
        if not file:
            response.simple_response('no file', 404)
        filename = secure_filename(file.filename)
        filename, file_extension = os.path.splitext(filename)
        new_filename = user.username+file_extension
        path_ = os.path.join(config.Config().UPLOAD_FOLDER_USER_PROFILE_IMAGES, new_filename)
        path = os.path.join(config.Config().PROJECT_ROOT, path_)
        file.save(path)
        user.profile_img_path = path
        db.session.commit()
        return response.simple_response('saved image')

    @auth.token_required
    def get(self, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {get} /users/images/ Get a profile pic
        @apiName GetProfilePic
        @apiGroup Users
        @apiUse TokenRequired
        @apiDescription Upload a profile pic.
        @apiUse BadRequest
        @apiUse NoSuchUserError
        """
        user_id = kwargs.get('user')['user_id']
        user = model.User.query.get(user_id)
        if not user:
            return response.simple_response('no such user', status=404)
        profile_img_path = user.profile_img_path
        print profile_img_path
        if not profile_img_path:
            return response.simple_response('no profile image uploaded yet', status=404)
        APP_ROOT = os.path.dirname(sys.modules['__main__'].__file__)
        return send_file(os.path.join(APP_ROOT, profile_img_path))

    @auth.token_required
    def delete(self, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {delete} /users/images/ Delete a profile pic
        @apiName DeleteProfilcePicture
        @apiGroup Users
        @apiUse TokenRequired
        @apiDescription Upload a profile pic.
        @apiUse BadRequest
        apiUse SuccessfullyDeleted
        @apiUse NoSuchUserError
        """
        user_id = kwargs.get('user')['user_id']
        user = model.User.query.get(user_id)
        if not user:
            return response.simple_response('no such user', status=404)
        profile_img_path = user.profile_img_path
        print profile_img_path
        if not profile_img_path:
            return response.simple_response('no profile image uploaded yet', status=404)
        APP_ROOT = os.path.dirname(sys.modules['__main__'].__file__)
        os.remove(os.path.join(APP_ROOT, profile_img_path))
        user.profile_img_path = None
        db.session.commit()
        return response.simple_response('deleted profile image')


api.add_resource(SingleUser, '/users/')
api.add_resource(ProfilePic, '/users/images/')


