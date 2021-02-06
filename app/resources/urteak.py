from app.db_connection import db
from flask_restx import Namespace, Resource, reqparse, inputs, fields
from flask_jwt import jwt_required

api = Namespace('years', description='')


parser = reqparse.RequestParser()
parser.add_argument('historial', required=False, default=False)

urteak_put_model = api.model('Urteak', {
    'urteak': fields.List(fields.Integer, description="Year list", required=True)
})


@api.route('/', strict_slashes=False)
class Years(Resource):
    @api.expect(parser, validate=True)
    def get(self):
        args = parser.parse_args()
        doc = db['years']
        result = doc.copy()
        del result['_id']
        del result['_rev']
        if args['historial'] and inputs.boolean(args['historial']):
            for k, v in doc.items():
                result[k] = [year for year in v if year > 2009]
        return result


@api.route('/<league>', strict_slashes=False, doc={'params':{'league': 'League ID'}} )
class YearsByLeague(Resource):

    def get(self, league):
        doc = db['years']
        years = doc.get(league)
        if years:
            return years
        else:
            return []

    @jwt_required()
    @api.expect(urteak_put_model, validate=True)
    def put(self, league):
        years_document = db['years'] 
        year_list = years_document.get(league)
        if year_list:
            years_document[league] = api.payload['urteak']
            years_document.save()
            return True
        else:
            return {"message": "Cannot update urteak"}, 400
