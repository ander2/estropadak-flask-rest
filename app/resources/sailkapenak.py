import logging
import app.config

from app.db_connection import get_db_connection
from flask_restx import Namespace, Resource, reqparse, fields
from flask_jwt import jwt_required

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
    'points': fields.Integer(description="Team points in league ranking", required=False, default=0),
    'position': fields.Integer(description="Team position in league ranking", required=False, default=0),
    'positions': fields.List(fields.Integer, description="List will all positions", required=False, default=[]),
    'cumulative': fields.List(fields.Integer, description="List will cumulative points thought league", required=False, default=[]),
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
    'league': fields.String(required=True, description="Ranking league", enum=app.config.LEAGUES),
    'year': fields.Integer(required=True, description="Ranking year")
})


class SailkapenakDAO:

    @staticmethod
    def get_sailkapena_by_league_year(league, year, category):
        with get_db_connection() as database:
            if league in ['gbl', 'bbl', 'btl', 'gtl']:
                _category = category.replace(' ', '_').lower()
                key = 'rank_{}_{}_{}'.format(league.upper(), year, _category)
            else:
                key = 'rank_{}_{}'.format(league.upper(), year)
            try:
                doc = database[key]
            except KeyError:
                return None
            result = [doc]
            return result

    @staticmethod
    def get_sailkapena_by_league(league):
        key = 'rank_{}'.format(league.upper())
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        endkey = "{}z".format(key)

        start = key
        end = endkey
        with get_db_connection() as database:
            try:
                ranks = database.get_view_result("estropadak", "rank",
                                raw_result=True,
                                startkey=start,
                                endkey=end,
                                include_docs=True,
                                reduce=False)
                result = []
                for rank in ranks['rows']:
                    result.append(rank['doc'])
                return result
            except KeyError:
                return {'error': 'Estropadak not found'}, 404
            return result

    @staticmethod
    def get_sailkapena_by_id(id: str):
        with get_db_connection() as database:
            try:
                return database[id]
            except KeyError:
                return None  # {'error': 'Sailkapena not found'}, 404

    @staticmethod
    def insert_sailkapena_into_db(sailkapena):
        with get_db_connection() as database:
            doc = database.create_document(sailkapena)
            return doc.exists()

    @staticmethod
    def update_sailkapena_into_db(sailkapena_id, sailkapena):
        with get_db_connection() as database:
            doc = database[sailkapena_id]
            stats = {}
            for s in sailkapena['stats']:
                stats[s['name']] = s['value']
            doc['stats'] = stats
            doc.save()

    @staticmethod
    def delete_sailkapena_from_db(sailkapena_id):
        with get_db_connection() as database:
            doc = database[sailkapena_id]
            if doc.exists():
                doc.fetch()
                doc.delete()

            
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


parser = reqparse.RequestParser()
parser.add_argument('league', type=str, required=True, choices=app.config.LEAGUES, case_sensitive=False)
parser.add_argument('year', type=int)
parser.add_argument('team', type=str, action="append", default=[])
parser.add_argument('category', type=str)


@api.route('/', strict_slashes=False)
class Sailkapenak(Resource):
    @api.expect(parser, validate=True)
    def get(self):
        stats = None
        args = parser.parse_args()
        if args.get('year') is None:
            stats = SailkapenakDAO.get_sailkapena_by_league(args['league'])
        else:
            if args.get('year') and args.get('year') < app.config.MIN_YEAR:
                return "Year not found", 400
            stats = SailkapenakDAO.get_sailkapena_by_league_year(args['league'], args['year'], args['category'])
        if stats is None:
            return []

        if len(args.get('team', [])) > 0:
            team_stats = []
            for stat in stats:
                try:
                    team_stats.append({
                        "id": stat['_id'],
                        "urtea": int(stat['_id'][-4:]),
                        "stats": { t: stat['stats'][t] for t in args['team'] }
                    })
                except KeyError as e:
                    logging.info('Team "%s" not found: %s', args['team'], e)
                    # return "Team not found", 400
            return team_stats
        else:
            result = [
                {
                    "id": stats[0]['_id'],
                    "urtea": args['year'],
                    "stats": stats[0]['stats']
                }
            ]
            return result


    @jwt_required()
    @api.expect(sailkapena_model, validate=True)
    def post(self):
        try:
            res = SailkapenakLogic.create_sailkapena(api.payload)
            if res:
                return {}, 201
            else:
                return {}, 400
        except Exception as e:
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
            stats = SailkapenakDAO.update_sailkapena_into_db(sailkapena_id, data)
            return stats
        except Exception as e:
            logging.info("Error", exc_info=1)
            return "Cannot update sailkapena", 400

    @jwt_required()
    def delete(self, sailkapena_id):
        SailkapenakDAO.delete_sailkapena_from_db(sailkapena_id)
