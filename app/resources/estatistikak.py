import couchdb
import logging
import app.config

from app.db_connection import db
from .utils import get_team_color
from flask_restx import Namespace, Resource, reqparse

api = Namespace('estatistikak', description='')


class EstatistikakDAO:
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
        result = doc
        return result

    @staticmethod
    def get_sailkapenak_by_league(league):
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


class EstatistikakLogic():

    @staticmethod
    def get_culumative_stats(league, year, team):
        result = []
        if year is None:
            sailkapenak = EstatistikakDAO.get_sailkapenak_by_league(league)
            for sailkapena in sailkapenak:
                urtea = int(sailkapena['_id'][-4:])
                try:
                    year_values = {
                        "key": urtea
                    }
                    values = [{"label": i, "value": val} for i, val in enumerate(sailkapena['stats'][team]['cumulative'])]
                    year_values["values"] = values
                    result.append(year_values)
                except KeyError:
                    pass
        else:
            sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, None)
            for taldea, stats in sailkapena['stats'].items():
                team_values = {
                    "key": taldea,
                    "color": get_team_color(taldea),
                }
                values = [{"label": i, "value": val} for i, val in enumerate(stats['cumulative'])]
                team_values["values"] = values
                result.append(team_values)
        return result

    @staticmethod
    def get_points_per_race(league: str, year: int):
        result = []
        sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, None)
        points_max = len(sailkapena['stats'])
        for taldea, stats in sailkapena['stats'].items():
            team_values = {
                "key": taldea,
                "color": get_team_color(taldea),
            }
            values = [{"label": i, "value": points_max - val + 1} for i, val in enumerate(stats['positions'])]
            team_values["values"] = values
            result.append(team_values)
        return result

    @staticmethod
    def get_rank(league: str, year: int):
        result = []
        sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, None)
        sorted_teams = sorted(sailkapena['stats'], key=lambda tal: sailkapena['stats'][tal]['points'], reverse=True)
        rank = {
            "key": 'Taldea',
            "values": [{
                "label": taldea,
                "color": get_team_color(taldea),
                "value": sailkapena['stats'][taldea]['points']
                } for taldea in sorted_teams
            ]
        }
        result.append(rank)
        return result

    @staticmethod
    def get_ages(league: str, year: int, team: str):
        result = []
        if team is None:
            sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, None)
            min_ages = {
                "key": 'Min',
                "values": [{
                    "label": taldea,
                    "value": val['age']['min_age']
                    } for taldea, val in sailkapena['stats'].items()
                ]
            }
            med_ages = {
                "key": 'Media',
                "values": [{
                    "label": taldea,
                    "value": val['age']['avg_age']
                    } for taldea, val in sailkapena['stats'].items()
                ]
            }
            max_ages = {
                "key": 'Max',
                "values": [{
                    "label": taldea,
                    "value": val['age']['max_age']
                    } for taldea, val in sailkapena['stats'].items()
                ]
            }
            result.append(min_ages)
            result.append(med_ages)
            result.append(max_ages)
        else:
            sailkapenak = EstatistikakDAO.get_sailkapenak_by_league(league)
            min_ages = {
                "key": 'Min',
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "value": sailkapena['stats'][team]['age']['min_age']
                    } for sailkapena in sailkapenak if team in sailkapena['stats'] and 'age' in sailkapena['stats'][team]
                ]
            }
            med_ages = {
                "key": 'Media',
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "value": sailkapena['stats'][team]['age']['avg_age']
                    } for sailkapena in sailkapenak if team in sailkapena['stats'] and 'age' in sailkapena['stats'][team]
                ]
            }
            max_ages = {
                "key": 'Max',
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "value": sailkapena['stats'][team]['age']['max_age']
                    } for sailkapena in sailkapenak if team in sailkapena['stats'] and 'age' in sailkapena['stats'][team]
                ]
            }
            result.append(min_ages)
            result.append(med_ages)
            result.append(max_ages)
        return result


parser = reqparse.RequestParser()
parser.add_argument('league', type=str, required=True, choices=app.config.LEAGUES, case_sensitive=False)
parser.add_argument('year', type=int)
parser.add_argument('team', type=str)
parser.add_argument('category', type=str)
parser.add_argument('stat', type=str, default='cumulative')


@api.route('/', strict_slashes=False)
class Estatistikak(Resource):
    @api.expect(parser, validate=True)
    def get(self):
        result = []
        args = parser.parse_args()
        year = args.get('year')
        team = args.get('team')
        league = args.get('league')
        stat_type = args.get('stat')
        if stat_type == 'cumulative':
            result = EstatistikakLogic.get_culumative_stats(league, year, team)
        elif stat_type == 'points':
            result = EstatistikakLogic.get_points_per_race(league, year)
        elif stat_type == 'rank':
            result = EstatistikakLogic.get_rank(league, year)
        elif stat_type == 'ages':
            result = EstatistikakLogic.get_ages(league, year, team)
        return result