from flask_restx import Namespace, Resource
from app.db_connection import db

api = Namespace('active_year', description='')


@api.route('/', strict_slashes=False)
class ActiveYear(Resource):
    def get(self):
        doc = db['active_year']
        return doc['year']
