from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse, marshal_with
from sqlalchemy.exc import IntegrityError
from flask_restful import marshal
from flask import jsonify
from app import db
import model
from app.validation import email as validator
from app.university import model as university_model
from app.user import model as user_model

group_blueprint = Blueprint('group', __name__)
api = Api(group_blueprint)


class SingleGroup(Resource):
    def put_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='you have to provide a user id')
        parser.add_argument('group_id', type=int, required=True, help='you have to provide a user id')
        parser.add_argument('group_password', type=str, default=None)
        parser.add_argument('description', type=str, default=None)
        parser.add_argument('topic_area', type=str, default=None)
        return parser

    def post_parser(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='you have to provide a user id')
        parser.add_argument('group_name', type=str, required=True, help='you have to provide a name for this group')
        parser.add_argument('topic_area', type=str, required=True, help='you have to provide a topic area for this group')
        parser.add_argument('password', type=str, default=None)
        parser.add_argument('description', type=str, required=True, help='you have to provide a description for this group')
        return parser

    def post(self):
        """
            create a new group and add the user to the list of members
        """
        parser = self.post_parser()
        args = parser.parse_args()
        user = user_model.User.query.get(args['user_id'])
        user_uni = university_model.University.query.get(user.university_id)
        if user and user_uni:
            new_group = model.Group(
                name=args['group_name'],
                topic_area= args['topic_area'],
                password=args['password'],
                description=args['description']
            )
            try:
                new_group.owner = user_uni
                db.session.add(new_group)
                new_group.members.append(user)
                db.session.commit()
                return make_response('group was added to the database', 201)
            except IntegrityError as error:
                s = ""
                if "Duplicate entry" in error.message:
                    s = "a group for this name already exists"
                    return make_response(s, 404)
                else:
                    s = "an error occured, the building could not be saved"
                    return make_response(s, 500)
        else:
            return make_response('no such user or university', 404)


    def put(self): # works
        """
            add a user to the group, update the groups description or topic area
        """
        parser = self.put_parser()
        args = parser.parse_args()
        message = ""
        # password protection check to come
        group_to_join = model.Group.query.get(args['group_id'])
        user = user_model.User.query.get(args['user_id'])
        if not (group_to_join or user):
            return make_response('no such user or group', 404)
        elif group_to_join and user and (user not in group_to_join.members):
            group_to_join.members.append(user)
            db.session.commit()
            message += 'user {user} added to group {group}. '.format(user=user.username,  group=group_to_join.name)
        for key, value in {k: v for k, v in args.iteritems() if 'id' not in k}.iteritems():
            if key and value:
                setattr(group_to_join, key, value)
                message += '{key} set to {value}. '.format(key=key, value=value)
            db.session.commit()
        return make_response(message, 200)


    def delete(self): pass
    # add route to delete one user from group


class GroupsAtUniversity(Resource):
    def get(self, university):
        groups_at_uni = university_model.University.query.filter_by(name=university).first()
        # members has 'joined' property so no need to load them separately into memory
        return marshal(groups_at_uni.groups.all(), model.Group.fields['with_members']) if groups_at_uni else make_response('no such group', 404)

class GroupWithId(Resource):
    def get(self, id):
        group = model.Group.query.get(id)
        return marshal(group, model.Group.fields['with_members']) if group else make_response('no such group', 404)



# !!! when returning a user list via group marshaller you have to explicitly load the relationship if dynamic='lazy' !!!
# !!! like so ... group.users ... another possiblity is to do lazy='joined' on the user object
api.add_resource(SingleGroup, '/groups/')
api.add_resource(GroupsAtUniversity, '/groups/<string:university>')
api.add_resource(GroupWithId, '/groups/<int:id>')
