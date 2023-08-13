import logging

from typing import List
from flask_restx import Namespace, Resource, reqparse, fields
from flask_jwt import jwt_required
from ..config import LEAGUES, MIN_YEAR
from ..dao.sailkapenak_dao import SailkapenakDAO

api = Namespace('sailkapenak', description='')
rower_model = api.model('Rowers rank data', {
    "altak": fields.Integer(description='New rowers in Team', required=True, default=0),
    "bajak": fields.Integer(description='Rowers lefting Team', required=True, default=0)
})
age_model = api.model('Ages rank data', {
    "min_age": fields.Integer(description='Min rower age in Team', required=False, default=0),
    "max_age": fields.Integer(description='Max rower age in Team', required=False, default=0),
    "avg_age": fields.Integer(description='Average rower age in Team', required=False, default=0)
})
rank_model = api.model('Team Rank', {
    'best': fields.Integer(description='Team\'s best position', required=False, default=0),
    'worst': fields.Integer(description='Team\'s worst position', required=False, default=0),
    'wins': fields.Integer(description='Races won by the Team', required=False, default=0),
    'points': fields.Float(description="Team points in league ranking", required=False, default=0),
    'position': fields.Integer(description="Team position in league ranking", required=False, default=0),
    'positions': fields.List(fields.Integer, description="List will all positions", required=False, default=[]),
    'cumulative': fields.List(
        fields.Float, description="List will cumulative points thought league", required=False, default=[]
    ),
    'rowers': fields.Nested(rower_model),
    'age': fields.Nested(age_model),
})
team_rank_model = api.model('Rank', {
    'name': fields.String(description='Team name', required=True),
    'value': fields.Nested(rank_model, required=False)
})
sailkapena_model = api.model('Sailkapena', {
    'id': fields.String(required=False, readonly=True),
    'stats': fields.List(fields.Nested(team_rank_model)),
    'league': fields.String(required=True, description="Ranking league", enum=LEAGUES),
    'year': fields.Integer(required=True, description="Ranking year")
})

sailkapenak_model = api.model('Sailkapenak', {
    'id': fields.String(required=False, readonly=True),
    'stats': fields.Nested(team_rank_model),
})

sailkapenak_list_model = api.model('Sailkapena listing model', {
    'docs': fields.List(fields.Nested(sailkapena_model)),
    'total': fields.Integer(example=1)
})


class SailkapenakLogic():

    @staticmethod
    def create_sailkapena(sailkapena):
        rank_id = f'rank_{sailkapena["league"]}_{sailkapena["year"]}'
        stats = {stat['name']: stat.get('value', {}) for stat in sailkapena['stats']}
        new_doc = {
            '_id': rank_id,
            'stats': stats
        }
        res = SailkapenakDAO.insert_sailkapena_into_db(new_doc)
        return res

    @staticmethod
    def get_sailkapenak(league: str, year: int, teams: List[str], category):
        stats = None
        if year is None:
            stats = SailkapenakDAO.get_sailkapena_by_league(league)
        else:
            if year and year < MIN_YEAR:
                return "Year not found", 400
            stats = SailkapenakDAO.get_sailkapena_by_league_year(league, year, category)
        if stats is None:
            return {'total': 0, 'docs': []}

        if len(teams) > 0:
            team_stats = SailkapenakDAO.get_sailkapenak_by_teams(league, year, teams)
            return team_stats

        else:
            res = []
            for stat in stats['docs']:
                res.append({
                    "id": stat['_id'],
                    "year": int(stat['_id'][-4:]),
                    "league": stat['_id'][5:9],
                    "stats": [{'name': k, 'value': v} for k, v in stat['stats'].items()]
                })
            result = {
                'total': stats['total'],
                'docs': res
            }
            return result

    @staticmethod
    def get_sailkapena_by_id(sailkapena_id):
        sailkapena = SailkapenakDAO.get_sailkapena_by_id(sailkapena_id)
        _, league, year = sailkapena_id.split('_')
        result = {
            'id': sailkapena['_id'],
            'league': league,
            'year': int(year),
            'stats': []
        }
        for k, v in sailkapena['stats'].items():
            result['stats'].append({
                'name': k,
                'value': v
            })
        return result

    @staticmethod
    def update_sailkapena(id, sailkapena):
        stats = {}
        for s in sailkapena['stats']:
            stats[s['name']] = s['value']
        data = {
            'stats': stats
        }
        SailkapenakDAO.update_sailkapena_into_db(id, data)


parser = reqparse.RequestParser()
parser.add_argument('league', type=str, required=True, choices=LEAGUES, case_sensitive=False)
parser.add_argument('year', type=int)
parser.add_argument('team', type=str, action="append", default=[])
parser.add_argument('category', type=str)


@api.route('/', strict_slashes=False)
class Sailkapenak(Resource):
    @api.expect(parser, validate=True)
    @api.marshal_with(sailkapenak_list_model, skip_none=True)
    def get(self):
        args = parser.parse_args()
        league = args['league']
        year = args['year']
        team = args['team']
        category = args['category']
        league = league.upper()
        return SailkapenakLogic.get_sailkapenak(league, year, team, category)

    @jwt_required()
    @api.expect(sailkapena_model, validate=True)
    def post(self):
        try:
            res = SailkapenakLogic.create_sailkapena(api.payload)
            if res:
                return {}, 201
            else:
                return {}, 400
        except Exception:
            logging.info("Error", exc_info=1)
            return {'message': "Cannot create sailkapena"}, 400


@api.route('/<string:sailkapena_id>')
class Sailkapena(Resource):

    @api.marshal_with(sailkapena_model)
    def get(self, sailkapena_id):
        stats = SailkapenakLogic.get_sailkapena_by_id(sailkapena_id)
        if stats is None:
            return "Sailkapenak not found", 404
        else:
            return stats

    @jwt_required()
    @api.expect(sailkapena_model, validate=True)
    def put(self, sailkapena_id):
        data = api.payload
        try:
            stats = SailkapenakLogic.update_sailkapena(sailkapena_id, data)
            return stats
        except Exception:
            logging.info("Error", exc_info=1)
            return "Cannot update sailkapena", 400

    @jwt_required()
    def delete(self, sailkapena_id):
        SailkapenakDAO.delete_sailkapena_from_db(sailkapena_id)
