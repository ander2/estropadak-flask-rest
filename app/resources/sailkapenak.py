import logging
import app.config

from app.db_connection import db
from flask_restx import Namespace, Resource, reqparse

api = Namespace('sailkapenak', description='')


class SailkapenakDAO:

    @staticmethod
    def get_sailkapena_by_league_year(league, year, category):
        if league == 'gbl' or league == 'bbl':
            _category = category.replace(' ', '_').lower()
            key = 'rank_{}_{}_{}'.format(league.upper(), year, _category)
        else:
            key = 'rank_{}_{}'.format(league.upper(), year)
        try:
            doc = db[key]
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
        try:
            ranks = db.get_view_result("estropadak", "rank",
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


parser = reqparse.RequestParser()
parser.add_argument('league', type=str, required=True, choices=app.config.LEAGUES, case_sensitive=False)
parser.add_argument('year', type=int)
parser.add_argument('team', type=str, action="append", default=[])
parser.add_argument('category', type=str)


@api.route('/', strict_slashes=False)
class Sailkapena(Resource):
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
