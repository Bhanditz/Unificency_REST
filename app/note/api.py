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

    def delete_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('note_id', type=int, required=True, help='you have to provide an id for this note')
        return parser

    def post(self):
        parser = self.post_parser()
        args = parser.parse_args()
        um = user_model.User
        parent_user = um.query.filter_by(email=args['user_email']).first()
        if not parent_user:
            make_response('no such user', 404)
        new_note = model.Note(
            args['name'], args['topic'], args['content']
        )
        new_note.owner = parent_user
        db.session.add(new_note)
        db.session.commit()
        make_response('note created', 201)

    def delete(self):
        # auth!
        parser = self.post_parser()
        args = parser.parse_args()
        note_to_delete = model.Note.query.get(id)
        if note_to_delete:
            db.session.delete(note_to_delete)
            db.session.commit()
            return make_response('user deleted', 200)
        return make_response('no such note', 404)

api.add_resource(NoteCreation, '/notes/')
api.add_resource(AllUniNotes, '/notes/<string:university>')