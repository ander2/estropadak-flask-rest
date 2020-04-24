import couchdb
import logging

from app.db_connection import db
from flask_restful import Resource, reqparse, inputs


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
        except couchdb.http.ResourceNotFound:
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
            ranks = db.view("estropadak/rank",
                                 None,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=True,
                                 reduce=False)
            result = []
            for rank in ranks.rows:
                result.append(rank.doc)
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404
        return result


class Sailkapena(Resource):
    def get(self):
        stats = None
        parser = reqparse.RequestParser()
        parser.add_argument('league', type=str)
        parser.add_argument('year', type=int)
        parser.add_argument('team', type=str)
        parser.add_argument('category', type=str)
        args = parser.parse_args()
        if args.get('year', None) is None:
            stats = SailkapenakDAO.get_sailkapena_by_league(args['league'])
        else:
            stats = SailkapenakDAO.get_sailkapena_by_league_year(args['league'], args['year'], args['category'])
        if stats is None:
            return []

        if args.get('team', None):
            team_stats = []
            for stat in stats:
                try:
                    _stats = stat['stats'][args['team']]
                    team_stats.append({
                        "id": stat.id,
                        "urtea": int(stat.id[-4:]),
                        "stats": {
                            args['team']: _stats
                        }
                    })
                except KeyError as e:
                    logging.info('Team "%s" not found' % args['team'])
            return team_stats
        else:
            result = [
                {
                    "id": stats[0].id,
                    "urtea": args['year'],
                    "stats": stats[0]['stats']
                }
            ]
            return result