from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse, fields, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import not_
from flask_restful import marshal
from flask import jsonify
from app import db
import model
from app.validation import auth
from app.university import model as university_model
from app.user import model as user_model
from app.group import model as group_model
from app.resources import response


group_blueprint = Blueprint('group', __name__)
api = Api(group_blueprint)


class CreateGroup(Resource):
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help='you have to provide a name for this group')
        parser.add_argument('topic_area', required=True, help='you have to provide a topic area for this group')
        parser.add_argument('password', default=None)
        parser.add_argument('description', required=True, help='you have to provide a description for this group')
        return parser

    @auth.token_required
    def post(self, **kwargs): # requires token
        """
        @apiVersion 0.1.0
        @apiUse TokenRequired
        @api {post} /groups/ Create a new group
        @apiName CreateGroup
        @apiGroup Groups
        @apiUse TokenRequired
        @apiDescription Create a new group.
        @apiParam {String} name A unique name for the group. You cant change this afterwards.
        @apiParam {String} topic_area A topic area which describes the purpose of this group.
        @apiParam {String} [password] The groups password.
        @apiParam {String} description A description for group.
        @apiUse UserAlreadyExistsError
        @apiUse BadRequest
        @apiUse SuccessfullyCreated
        @apiUse ResourceAlreadyExistsError
        @apiUse CouldNotBeSavedError
        """
        parser = self.post_parser()
        args = parser.parse_args()
        user = kwargs.get('user')
        user_info = user_model.User.query.get(user['user_id'])
        user_uni = university_model.University.query.get(user_info.university_id)
        if user_info and user_uni:
            new_group = model.Group(
                name=args['name'],
                topic_area= args['topic_area'],
                description=args['description']
            )
            try:
                if args['password']:
                    new_group.hash_password(args['password'])
                new_group.owner = user_uni
                db.session.add(new_group)
                new_group.members.append(user_info)
                db.session.commit()
                return make_response(jsonify({'message': 'added group to database'}), 201)
            except IntegrityError as error:
                db.session.rollback();
                s = ""
                if "Duplicate entry" in error.message:
                    s = "a group for this name already exists"
                    return make_response(jsonify({'message':s}), 409)
                else:
                    s = "an error occured, the building could not be saved"
                    return make_response(jsonify({'message':s}), 500)
        else:
            return make_response(jsonify({'message':'no such group or university'}), 404)


class UpdateGroup(Resource):
    def put_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('password', default=None)
        parser.add_argument('description', default=None)
        parser.add_argument('topic_area', default=None)
        return parser

    @auth.token_required
    def put(self, group_id, *args, **kwargs): # works # requires token
        """
        @apiVersion 0.1.0
        @api {put} /groups/{group_id}/ Modify a group
        @apiName ModifyGroup
        @apiGroup Groups
        @apiDescription Modify a group. Note that you have to provide Token and the user must be a member of this group.
        @apiParam {String} [topic_area] A topic area which describes the purpose of this group.
        @apiParam {String} [description] A description for group.
        @apiUse TokenRequired
        @apiUse NoSuchUserError
        @apiUse BadRequest
        @apiSuccess 200 ModifiedGroup was successfully modified.
        @apiSuccessExample ModifiedGroup:
          HTTP/1.1 200 OK
          {
            "message:""({key} set to {value})*"
            }
        """
        user = kwargs.get('user')
        parser = self.put_parser()
        args = parser.parse_args()
        message = u""
        # password protection check to come
        user = user_model.User.query.get(user['user_id'])
        group_to_join = [group for group in user.groups if group.id == group_id]
        if not (group_to_join or user):
            return make_response(jsonify({'message': 'you need to be a member of this group in order to modify its data'}), 404)
        for key, value in {k: v for k, v in args.iteritems() if 'id' not in k}.iteritems():
            value = unicode(value)
            if key and value:
                setattr(group_to_join[0], key, value)
                message += u'{key} set to {value}. '.format(key=key, value=value)
            db.session.commit()
        return make_response(jsonify({'message': message}))


    def delete(self): pass
    # add route to delete one user from group


class JoinGroup(Resource):
    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('password')
        return parser

    @auth.token_required
    def post(self, group_id, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {post} /groups/{group_id}/join/ Join a group
        @apiName JoinGroup
        @apiGroup Groups
        @apiDescription Join a group. Note that you have to provide a token.
        @apiParam {String} [password] If the group is password protected, provide a password.
        @apiUse TokenRequired
        @apiUse NoSuchUserError
        @apiUSe ResourceAlreadyExistsError
        @apiUse BadRequest
        @apiSuccess 200 JoinedGroup You successfully joined the group.
        @apiSuccessExample ModifiedGroup:
          HTTP/1.1 200 OK
          {
            "message:""user {username} added to group {groupname}"
            }
        """
        args = self.post_parser().parse_args()
        user = kwargs.get('user')
        requesting_user = user_model.User.query.get(user['user_id'])
        group_to_join = model.Group.query.get(group_id)
        if not group_to_join :
            return make_response(jsonify({'message':'This group does not exist'}),404)
        if not requesting_user:
            return make_response(jsonify({'message': 'This user does not exist'}), 404)
        if group_to_join in requesting_user.groups:
            return make_response(jsonify({'message': 'You are already a member of this group'}), 409)
        if group_to_join.password_hash:
            if not args['password']:
                return make_response(jsonify({'message': 'This group is password protected, please provide a password'}), 401)
            if group_to_join.verify_password(args['password']):
                group_to_join.members.append(requesting_user)
                db.session.commit()
                return make_response(jsonify({'message': 'Added {user} to {group}'.format(user=requesting_user.username,group=group_to_join.name)}))
            else:
                return make_response((jsonify({'message': 'The password you provided was wrong'})),401)
        else:
            group_to_join.members.append(requesting_user)
            db.session.commit()
            return make_response(jsonify(
                {'message': 'Added {user} to {group}'.format(user=requesting_user.username, group=group_to_join.name)}))


class LeaveGroup(Resource):

    @auth.token_required
    def post(self, group_id, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {post} /groups/{group_id}/leave/ Leave a group
        @apiName LeaveGroup
        @apiGroup Groups
        @apiDescription Leave a group. Note that you have to provide a token.
        @apiUse TokenRequired
        @apiUse NoSuchUserError
        @apiUSe ResourceAlreadyExistsError
        @apiUse BadRequest
        @apiSuccess 200 JoinedGroup You successfully joined the group.
        @apiSuccessExample ModifiedGroup:
          HTTP/1.1 200 OK
          {
            "message:" "({key} set to {value} | )*"
            }
        """
        user = kwargs.get('user')
        requesting_user = user_model.User.query.get(user['user_id'])
        group_to_leave = model.Group.query.get(group_id)
        if not group_to_leave :
            return make_response(jsonify({'message':'This group does not exist'}), 404)
        if not requesting_user:
            return make_response(jsonify({'message': 'This user does not exist'}), 404)
        if not (group_to_leave in requesting_user.groups):
            return make_response(jsonify({'message': 'You are not a member of this group'}), 401)
        group_to_leave.members.remove(requesting_user)
        db.session.commit()
        return make_response(jsonify({'message': '{user} left {group}'.format(user=requesting_user.username,
                                                                              group=group_to_leave.name)}))


class GroupsAtUniversity(Resource):
    @auth.token_required
    def get(self, university, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {get} /groups/{university}?isMember={true/false} Get all groups at a university.
        @apiName GetGroupsAtUniversity
        @apiDescription Returns a list of all groups at the specified university or, if you provide the parameter isMember
        you will receive a list of groups you are (not) a member of.
        @apiGroup Groups
        @apiUse TokenRequired
        @apiUse BadRequest
        @apiSuccess 200 message Success message.
        @apiSuccessExample Success-Response:
          HTTP/1.1 200 OK
          {
            'id': the groups id,
            'name': the groups name,
            'topic_area': the groups area of topic
            }

        @apiError NoSuchResourceError

        """
        user_id = kwargs.get('user')['user_id']
        user = user_model.User.query.get(user_id)
        uni = university_model.University.query.filter_by(name=university).first()
        if not uni:
            return response.simple_response('no such university')
        all_groups = uni.groups
        is_member = request.args.get('isMember')
        if is_member:
            if is_member.lower() == 'true':
                return jsonify(marshal(user.groups, model.Group.fields['only_id_and_name']))
            elif is_member.lower() == 'false':
                #user not in uni.groups
                g = all_groups.filter(
                    ~group_model.Group.members.any(user_model.User.id == user_id)
                ).order_by(model.Group.id.desc()).all()
                return jsonify(marshal(g, model.Group.fields['only_id_and_name']))
            else:
                return response.simple_response('expected is_member to be true or false, got {0}'.format(is_member), status=400)
        all_groups = all_groups.all()
        return jsonify(marshal(all_groups, model.Group.fields['only_id_and_name']))\
            if user and all_groups else response.simple('no such group or user', status=404)


class GroupWithId(Resource): # works
    @auth.token_required
    def get(self, id, *args, **kwargs):
        """
        @apiVersion 0.1.0
        @api {get} /groups/{id}/ Get group at id.
        @apiName GetGroupAtId
        @apiGroup Groups
        @apiUse TokenRequired
        @apiUse BadRequest
        @apiSuccess 200 message Success message for group creation.
        @apiSuccessExample Success-Response:
          HTTP/1.1 200 OK
          {
            'id': the groups id,
            'name': the groups name,
            'topic_area': the groups area of topic,
            'description': the groups description,
             'protected':  true/false if the group is password protected,
            'members': [{name: users who are members of the group}]
            }

        @apiUse NoSuchResourceError

        """
        user_id = kwargs.get('user')['user_id']
        user = user_model.User.query.get(user_id)
        group = group_model.Group.query.get(id)
        if user and group:
            cpy = group_model.Group.fields['with_members'].copy()
            cpy.update({'im_a_member': fields.Boolean(attribute=lambda x: True if user in group.members else False)})
            return jsonify(marshal(group, cpy))
        return response.simple_response('no such group or user', status=404)


api.add_resource(CreateGroup, '/groups/')
api.add_resource(GroupsAtUniversity, '/groups/<string:university>/')
api.add_resource(GroupWithId, '/groups/<int:id>/')
api.add_resource(JoinGroup,'/groups/<int:group_id>/join/')
api.add_resource(UpdateGroup,'/groups/<int:group_id>/')
api.add_resource(LeaveGroup,'/groups/<int:group_id>/leave/')
