from app.db_connection import db
from flask_restx import Namespace, Resource, reqparse, inputs

api = Namespace('years', description='')


parser = reqparse.RequestParser()
parser.add_argument('historial', required=False, default=False)


@api.route('/', strict_slashes=False)
class Years(Resource):
    @api.expect(parser, validate=True)
    def get(self):
        args = parser.parse_args()
        doc = db['years']
        del doc['_id']
        del doc['_rev']
        if args['historial'] and inputs.boolean(args['historial']):
            for k, v in doc.items():
                doc[k] = [year for year in v if year > 2009]
        return doc
