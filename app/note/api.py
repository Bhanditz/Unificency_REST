from flask import Blueprint, make_response
from flask_restful import Api, Resource, marshal_with, reqparse, marshal
from sqlalchemy.exc import IntegrityError
from flask_restful import fields
from flask import jsonify
from app import db
import model
from app.user import model as user_model
from app.group import model as group_model
from app.validation import email


note_blueprint = Blueprint('note', __name__)
api = Api(note_blueprint)

# all notes from a group with id
class GroupNotes(Resource):
    def get(self, group_id):
        """
        @apiVersion 0.1.0
        @api {get} /notes/{group_id} Get a groups notes.
        @apiName GetGroupNotes
        @apiGroup Notes
        @apiDescription Get a groups notes.
        @apiUse BadRequest
        @apiSuccess 200 Success-Response:
        @apiSuccessExample Success-Response
          HTTP/1.1 200 OK
          {
            [
            {
            'name': the groups name,
            'topic': the groups topic,
            'content': the groups content
            }, ...]
            }

        """
        group_with_id = group_model.Group.query.get(group_id)
        if group_with_id:
            return marshal(group_with_id.notes, model.Note.fields)
        return make_response('no notes found', 404)

    def delete(self, id):
        """
        @apiVersion 0.1.0
        @api {delete} /notes/{id} Delete a note.
        @apiName DeleteNote
        @apiGroup Notes
        @apiDescription Delete a note.
        @apiUse BadRequest
        @apiSuccess 200 Success-Response:
        @apiUse NoSuchResourceError
        @apiUse SuccessfullyDeleted
        """
        # auth! !adjust to id
        parser = self.post_parser()
        args = parser.parse_args()
        note_to_delete = model.Note.query.get(id)
        if note_to_delete:
            db.session.delete(note_to_delete)
            db.session.commit()
            return make_response('user deleted', 200)
        return make_response('no such note', 404)


class NoteCreation(Resource):
    # how the post request for this route looks like
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='you have to provide a user id for this note')
        parser.add_argument('group_id', type=int, required=True, help='you have to provide a group id for this note')
        parser.add_argument('name', type=str, required=True, help='you have to provide a name for this note')
        parser.add_argument('topic', type=str, required=True, help='you have to provide a topic for this note')
        parser.add_argument('content', type=str, required=True, help='you have to provide some content for this room')
        return parser

    def delete_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('note_id', type=int, required=True, help='you have to provide an id for this note')
        return parser

    def post(self):#note.creator und note.group
        """
        @apiVersion 0.1.0
        @api {post} /notes/ Create a note.
        @apiName CreateNote
        @apiGroup Notes
        @apiDescription Create a new Note.
        @apiUse BadRequest
        @apiUse SuccessfullyCreated
        @apiParam {Number} user_id Unique id for the user who tries to create a new note.
        @apiParam {Number} group_id A unique id for the group in which the note is posted.
        @apiParam {String} name The notes name.
        @apiParam {String} content The notes content.
        @apiUse NoSuchUserError
        @apiUse CouldNotBeSavedError
        """
        parser = self.post_parser()
        args = parser.parse_args()
        um = user_model.User
        post_in_group = group_model.Group.get(args['group_id'])
        parent_user = um.query.get(args['user_id'])
        if not parent_user or not post_in_group:
            return make_response('no such user', 404)
        new_note = model.Note(
            args['name'], args['topic'], args['content']
        )
        new_note.creator = parent_user
        new_note.group = post_in_group
        db.session.add(new_note)
        db.session.commit()
        return make_response('note created', 201)


api.add_resource(NoteCreation, '/notes')
api.add_resource(GroupNotes, '/notes/<int:id>')