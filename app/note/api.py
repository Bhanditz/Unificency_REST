from flask import Blueprint, make_response
from flask_restful import Api, Resource, marshal_with, reqparse
from sqlalchemy.exc import IntegrityError
from flask_restful import fields
from flask import jsonify
from app import db
import model
from app.user import model as user_model
from app.validation import email


note_blueprint = Blueprint('room', __name__)
api = Api(note_blueprint)


class AllUniNotes(Resource):
    def get(self, university):
        pass


class NoteCreation(Resource):
    # how the post request for this route looks like
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_email', type=email, required=True, help='you have to provide an email for this note')
        parser.add_argument('name', type=str, required=True, help='you have to provide a name for this note')
        parser.add_argument('topic', type=str, required=True, help='you have to provide a topic for this note')
        parser.add_argument('content', type=str, required=True, help='you have to provide some content for this room')
        return parser

    """def post(self):
        parser = self.post_parser()
        args = parser.parse_args()
        um = user_model.User
        parent_user = um.query.filter_by(email=args['user_email']).one()
        if not parent_user:
            make_response('no such user found', 404)
        parent_user.notes.appen(model.Note(
            args['name'], args['topic'], args['content']
        ))"""


api.add_resource(NoteCreation, '/notes/')
api.add_resource(AllUniNotes, '/notes/<string:university>')