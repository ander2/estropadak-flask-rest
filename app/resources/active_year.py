from flask_restx import Namespace, Resource
from app.db_connection import get_db_connection

api = Namespace('active_year', description='')


@api.route('/', strict_slashes=False)
class ActiveYear(Resource):
    def get(self):
        with get_db_connection() as database:
            doc = database['active_year']
            return doc['year']
