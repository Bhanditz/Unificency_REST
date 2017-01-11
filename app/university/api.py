from flask import Blueprint, make_response
from flask_restful import Api, Resource
from flask_restful import marshal
import model

university_blueprint = Blueprint('university', __name__)
api = Api(university_blueprint)


class UniList(Resource):
    def get(self):
        """
        @apiVersion 0.1.0
        @api {post} /universities/ Get all universities
        @apiName GetAllUnis
        @apiGroup Universities
        @apiDescription Returns a list of all universities in the database.
        @apiUse NoSuchResourceError
        @apiSuccess AllUnisSuccess
        @apiSuccess {Number} id The unis id.
        @apiSuccess {String}  name The unis name.
        @apiSuccess {Number}  city The city the uni is located.
        @apiSuccess {String}  country The country the uni is located
        @apiSuccessExample AllUnisSuccess:
          HTTP/1.1 200 OK
          {
            [{"id:" "The unis id",
            "name:" "The unis name",
            "city:" "The city the uni is located",
            "country:" "The country the uni is located"
            },...]
        """
        all_universities = model.University.query.all()
        if all_universities:
            return marshal(all_universities, model.University.fields['basic'])
        return make_response('no universities found')


api.add_resource(UniList, '/universities/')
