import app.config

from app.db_connection import get_db_connection
from .utils import get_team_color
from flask_restx import Namespace, Resource, reqparse
from .estropadak import EstropadakDAO

api = Namespace('estatistikak', description='')


class EstatistikakDAO:
    @staticmethod
    def get_sailkapena_by_league_year(league, year, category):
        if league in ['gbl', 'bbl', 'btl', 'gtl']:
            _category = category.replace(' ', '_').lower()
            key = 'rank_{}_{}_{}'.format(league.upper(), year, _category)
        else:
            key = 'rank_{}_{}'.format(league.upper(), year)
        with get_db_connection() as database:
            try:
                doc = database[key]
            except KeyError:
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


class EstatistikakLogic():

    @staticmethod
    def get_culumative_stats(league, year, team, category):
        result = []
        if year is None:
            sailkapenak = EstatistikakDAO.get_sailkapenak_by_league(league)
            for sailkapena in sailkapenak:
                urtea = int(sailkapena['_id'][-4:])
                try:
                    year_values = {
                        "key": team
                    }
                    values = [{
                        "label": urtea,
                        "x": i,
                        "value": val }
                        for i, val in enumerate(sailkapena['stats'][team]['cumulative'])]
                    year_values["values"] = values
                    result.append(year_values)
                except KeyError:
                    pass
        else:
            sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, category)
            estropadak = EstropadakDAO.get_estropadak_by_league_year(
                league,
                year)
            estropadak = [estropada for estropada in estropadak if not estropada['izena'].startswith('Play')]
            for taldea, stats in sailkapena['stats'].items():
                team_values = {
                    "key": taldea,
                    "color": get_team_color(taldea),
                }
                values = [{"label": val[1]['izena'],
                           "x": i,
                           "value": val[0]}
                          for i, val in enumerate(zip(stats['cumulative'], estropadak))]
                team_values["values"] = values
                result.append(team_values)
        try:
            result = sorted(result, key=lambda x: x['values'][-1]['value'])
        except IndexError:
            pass
        return result

    @staticmethod
    def get_points_per_race(league: str, year: int, category: str):
        result = []
        sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, category)
        estropadak = EstropadakDAO.get_estropadak_by_league_year(
            league,
            year)
        estropadak = [estropada for estropada in estropadak if not estropada['izena'].startswith('Play')]
        points_max = len(sailkapena['stats'])
        for taldea, stats in sailkapena['stats'].items():
            team_values = {
                "key": taldea,
                "color": get_team_color(taldea),
            }
            values = [{
                "label": val[1]['izena'],
                "x": i,
                "value": points_max - val[0] + 1}
                for i, val in enumerate(zip(stats['positions'], estropadak))]
            team_values["values"] = values
            result.append(team_values)
        return result

    @staticmethod
    def get_points(league: str, team: str):
        result = []
        sailkapenak = EstatistikakDAO.get_sailkapenak_by_league(league)
        rank = {
            "key": team,
            "values": [{
                "label": int(sailkapena['_id'][-4:]),
                "x": int(sailkapena['_id'][-4:]),
                "color": get_team_color(team),
                "value": sailkapena['stats'][team]['points']
                } for sailkapena in sailkapenak if team in sailkapena['stats']
            ]
        }
        result.append(rank)
        return result

    @staticmethod
    def get_rank(league: str, year: int, team: str, category: str):
        result = []
        if team is None:
            sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, category)
            sorted_teams = sorted(sailkapena['stats'], key=lambda tal: sailkapena['stats'][tal]['position'], reverse=False)
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
        else:
            sailkapenak = EstatistikakDAO.get_sailkapenak_by_league(league)
            rank = {
                "key": team,
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "color": get_team_color(team),
                    "value": sailkapena['stats'][team]['position']
                    } for sailkapena in sailkapenak if team in sailkapena['stats']
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

    @staticmethod
    def get_incorporations(league: str, year: int, team: str):
        result = []
        if team is None:
            sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, None)
            altak = {
                "key": 'Altak',
                "values": [{
                    "label": taldea,
                    "value": val['rowers']['altak']
                    } for taldea, val in sailkapena['stats'].items() if 'rowers' in sailkapena['stats'][taldea]
                ]
            }
            bajak = {
                "key": 'Bajak',
                "values": [{
                    "label": taldea,
                    "value": val['rowers']['bajak']
                    } for taldea, val in sailkapena['stats'].items() if 'rowers' in sailkapena['stats'][taldea]
                ]
            }
            result.append(altak)
            result.append(bajak)
        else:
            sailkapenak = EstatistikakDAO.get_sailkapenak_by_league(league)
            altak = {
                "key": 'Altak',
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "value": sailkapena['stats'][team]['rowers']['altak']
                    } for sailkapena in sailkapenak if team in sailkapena['stats'] and 'rowers' in sailkapena['stats'][team]
                ]
            }
            bajak = {
                "key": 'Bajak',
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "value": sailkapena['stats'][team]['rowers']['bajak']
                    } for sailkapena in sailkapenak if team in sailkapena['stats'] and 'rowers' in sailkapena['stats'][team]
                ]
            }
            result.append(altak)
            result.append(bajak)
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
        category = args.get('category')
        stat_type = args.get('stat')
        if stat_type == 'cumulative':
            result = EstatistikakLogic.get_culumative_stats(league, year, team, category)
        elif stat_type == 'points':
            if team:
                result = EstatistikakLogic.get_points(league, team)
            else:
                result = EstatistikakLogic.get_points_per_race(league, year, category)
        elif stat_type == 'rank':
            result = EstatistikakLogic.get_rank(league, year, team, category)
        elif stat_type == 'ages':
            result = EstatistikakLogic.get_ages(league, year, team)
        elif stat_type == 'incorporations':
            result = EstatistikakLogic.get_incorporations(league, year, team)
        return result
