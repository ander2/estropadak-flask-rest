from app.db_connection import get_db_connection
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


class YearsDAO:
    @staticmethod
    def get_years_from_db():
        with get_db_connection() as database:
            return database['years']

    @staticmethod
    def update_years_into_db(years, league):
        with get_db_connection() as database:
            doc = database['years']
            if league:
                doc[league] = years
            else:
                doc = years
            doc.save()

@api.route('/', strict_slashes=False)
class Years(Resource):
    @api.marshal_with(urtea_model, as_list=True)
    def get(self):
        args = parser.parse_args()
        all_years = YearsDAO.get_years_from_db()
        result = []
        for k, v in all_years.items():
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
        all_years = YearsDAO.get_years_from_db()
        years = all_years.get(league, [])
        return {
            'name': league,
            'years': years
        }

    @jwt_required()
    @api.expect(urteak_put_model, validate=True)
    def put(self, league):
        YearsDAO.update_years_into_db(api.payload['urteak'], league)
