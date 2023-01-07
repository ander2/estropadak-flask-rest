from flask_restx import Namespace, Resource, fields
from .common.parsers import required_league_year_parser
from ..dao.taldeak_dao import TaldeakDAO
from ..dao.plantilak_dao import PlantilakDAO

api = Namespace('taldeak', description='')

taldeak_model = api.model('Taldea', {
    'name': fields.String(required=True),
    'alt_names': fields.List(fields.String, required=False),
    'short': fields.String(required=False),
})


@api.route('/', strict_slashes=False)
class Taldeak(Resource):
    @api.expect(required_league_year_parser, validate=True)
    def get(self):
        args = required_league_year_parser.parse_args()
        teams = []
        league = args.get('league')
        year = args.get('year')
        category = args.get('category')
        if league.upper() not in ('GBL', 'GTL', 'BBL', 'BTL'):
            category = None
        teams = TaldeakDAO.get_taldeak(league, year, category)
        return teams


@api.route('/<team>')
class Plantilla(Resource):
    @api.expect(required_league_year_parser)
    def get(self, team):
        args = required_league_year_parser.parse_args()
        leagues = ['ACT', 'ARC1', 'ARC2', 'ETE', 'EUSKOTREN']
        league = args['league'].upper()
        if league not in leagues:
            return {'message': 'Not valid league'}, 400
        team = PlantilakDAO.get_plantila(team, league, args['year'])
        if team is None:
            return {'message': 'Team not found'}, 404
        return team
