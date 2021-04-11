from app.db_connection import db
import app.config
from flask_restx import Namespace, Resource, reqparse, inputs, fields
from flask_jwt import jwt_required

api = Namespace('years', description='')


parser = reqparse.RequestParser()
parser.add_argument('historial', required=False, default=False)

urteak_put_model = api.model('Urteak PUT model', {
    'urteak': fields.List(fields.Integer, description="Year list", required=True)
})

urtea_model = api.model('Urtea', {
    'name': fields.String(description="League name", example="ACT"),
    'years': fields.List(fields.Integer, description="Year list", required=True, example=[2010, 2011, 2012])
})


@api.route('/', strict_slashes=False)
class Years(Resource):
    @api.marshal_with(urtea_model, as_list=True)
    def get(self):
        args = parser.parse_args()
        doc = db['years']
        result = []
        for k, v in doc.items():
            if k.upper() in app.config.LEAGUES or k == 'euskotren':
                if args['historial'] and inputs.boolean(args['historial']):
                    if args['year'] > 2009:
                        result.append({
                            'name': k,
                            'years': v
                        })
                else:
                    result.append({
                        'name': k,
                        'years': v
                    })
        return result


@api.route('/<league>', strict_slashes=False, doc={'params': {'league': 'League ID'}} )
class YearsByLeague(Resource):

    @api.marshal_with(urtea_model)
    def get(self, league):
        doc = db['years']
        years = doc.get(league, [])
        return {
            'name': league,
            'years': years
        }

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
