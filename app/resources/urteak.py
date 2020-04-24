from app.db_connection import db
from flask_restful import Resource, reqparse, inputs


class Years(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('historial', required=False, default=False)
        args = parser.parse_args()
        doc = db['years']
        del doc['_id']
        del doc['_rev']
        if args['historial'] and inputs.boolean(args['historial']):
            for k, v in doc.items():
                doc[k] = [year for year in v if year > 2009]
        return doc
