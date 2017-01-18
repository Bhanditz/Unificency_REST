from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse, marshal
from flask import jsonify
from app import db
import model
from app.user import model as user_model
from app.group import model as group_model
from app.resources import response
from app.validation import auth


note_blueprint = Blueprint('note', __name__)
api = Api(note_blueprint)

class NoteCRUD(Resource):
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('content', required=True, help='you have to provide some content for this note')
        parser.add_argument('name', type=str, required=True, help='you have to provide a name for this note')
        parser.add_argument('topic', type=str, required=True, help='you have to provide a topic for this note')
        return parser

    @auth.token_required
    def post(self, group_id, *args, **kwargs):#note.creator und note.group
        """
        @apiVersion 0.1.0
        @api {post} /notes/{group_id}/create/ Create a note.
        @apiName CreateNote
        @apiGroup Notes
        @apiDescription Create a new Note.
        @apiUse TokenRequired
        @apiUse BadRequest
        @apiUse SuccessfullyCreated
        @apiParam {String} name The notes name.
        @apiParam {String} topic The notes topic.
        @apiParam {String} content The notes content.
        @apiUse NoSuchUserError
        @apiUse CouldNotBeSavedError
        """

        user_id = kwargs.get('user')['user_id']
        parser = self.post_parser()
        args = parser.parse_args()
        post_in_group = group_model.Group.query.get(group_id)
        parent_user = user_model.User.query.get(user_id)
        if not parent_user or not post_in_group:
            return response.simple_response('no such user or group', status=404)
        if not parent_user.is_member_of(post_in_group):
            return response.simple_response('you must be a member of this group', status=401)
        new_note = model.Note(
            args['name'], args['topic'], args['content']
        )
        new_note.creator = parent_user
        new_note.group = post_in_group
        db.session.add(new_note)
        db.session.commit()
        return response.simple_response('note created', status=201)

    @auth.token_required
    def get(self, group_id, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {get} /notes/{group_id}/ Get a groups notes.
        @apiName GetGroupNotes
        @apiGroup Notes
        @apiUse TokenRequired
        @apiDescription Get a groups notes.
        @apiUse BadRequest
        @apiSuccess 200 Success-Response:
        @apiSuccessExample Success-Response
          HTTP/1.1 200 OK
          {
            [
            {
            'id': the notes id,
            'creator': the creators name,
            'group': the groups name the note was posted in,
            'name': the groups name,
            'topic': the groups topic,
            'content': the groups content
            }, ...]
            }

        """
        user_id = kwargs.get('user')['user_id']
        user = user_model.User.query.get(user_id)
        group = group_model.Group.query.get(group_id)
        if user and group:
            if user.is_member_of(group):
                # explicitly load because of lazy relationship
                notes = group.notes.all()
                return marshal(notes, model.Note.fields)
            else:
                return make_response(jsonify({'message':'no you are not a member of this group'}), 404)
        return response.simple_response('no notes found', status=404)

class DeleteById(Resource):
    @auth.token_required
    def delete(self, id_, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {delete} /notes/{note_id}/ Delete a note.
        @apiName DeleteNote
        @apiGroup Notes
        @apiUse TokenRequired
        @apiDescription Delete a note.
        @apiUse BadRequest
        @apiSuccess 200 Success-Response:
        @apiUse NoSuchResourceError
        @apiUse SuccessfullyDeleted
        """
        user_id = kwargs.get('user')['user_id']
        user = user_model.User.query.get(user_id)
        note_to_delete = model.Note.query.get(id_)
        if not user or not note_to_delete:
            return response.simple_response('no such note or user', status=404)
        if note_to_delete in user.notes:
            db.session.delete(note_to_delete)
            db.session.commit()
            return response.simple_response('note deleted')
        return response.simple_response('you must be the creator of this note in order to delete it', status=401)


api.add_resource(NoteCRUD, '/notes/<int:group_id>')
api.add_resource(DeleteById, '/notes/<int:id_>/')
