import logging

from .common.utils import get_team_color
from flask_restx import Namespace, Resource
from .common.parsers import estatistikak_parser
from .estropadak import EstropadakDAO
from ..dao.estatistikak_dao import EstatistikakDAO

api = Namespace('estatistikak', description='')


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
                        "value": val}
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
            estropadak = [
                estropada for estropada in estropadak['docs']
                if not estropada['izena'].startswith('Play')
                and estropada.get('puntuagarria', True)
            ]
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
        return {
            'total': len(result),
            'docs': result
        }

    @staticmethod
    def get_points_per_race(league: str, year: int, category: str):
        result = []
        sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, category)
        estropadak = EstropadakDAO.get_estropadak_by_league_year(
            league,
            year)
        estropadak = [estropada for estropada in estropadak['docs'] if not estropada['izena'].startswith('Play')]
        if sailkapena:
            points_max = len(sailkapena['stats'])
            for taldea, stats in sailkapena['stats'].items():
                team_values = {
                    "key": taldea,
                    "color": get_team_color(taldea),
                }
                if not category:
                    values = [{
                        "label": val[1]['izena'],
                        "x": i,
                        "value": points_max - val[0] + 1}
                        for i, val in enumerate(zip(stats['positions'], estropadak))]
                else:
                    points_max = stats['points'] + stats.get('discard', 0)
                    points = []
                    cumulative = [0] + stats['cumulative']
                    for i, point in enumerate(cumulative):
                        try:
                            points.append(cumulative[i + 1] - point)
                        except Exception:
                            # points.append(points_max - point)
                            break
                    values = [{
                        "label": val[1]['izena'],
                        "x": i,
                        "value": val[0]}
                        for i, val in enumerate(zip(points, estropadak))]
                    # }]

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
            sorted_teams = sorted(
                sailkapena['stats'],
                key=lambda tal: sailkapena['stats'][tal]['position'],
                reverse=False)
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
        logging.info(f'Got team {league} {year} {team}')
        if team is None:
            sailkapena = EstatistikakDAO.get_sailkapena_by_league_year(league, year, None)
            if not sailkapena or not sailkapena.get('stats', []):
                return result
            logging.info('Got sailkapena')
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
                } for sailkapena in sailkapenak if team in sailkapena['stats']
                           and 'age' in sailkapena['stats'][team]]
            }
            med_ages = {
                "key": 'Media',
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "value": sailkapena['stats'][team]['age']['avg_age']
                } for sailkapena in sailkapenak if team in sailkapena['stats']
                           and 'age' in sailkapena['stats'][team]]
            }
            max_ages = {
                "key": 'Max',
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "value": sailkapena['stats'][team]['age']['max_age']
                } for sailkapena in sailkapenak if team in sailkapena['stats']
                           and 'age' in sailkapena['stats'][team]]
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
                    "label":
                    int(sailkapena['_id'][-4:]),
                    "value":
                    sailkapena['stats'][team]['rowers']['altak']
                } for sailkapena in sailkapenak if team in sailkapena['stats']
                           and 'rowers' in sailkapena['stats'][team]]
            }
            bajak = {
                "key": 'Bajak',
                "values": [{
                    "label": int(sailkapena['_id'][-4:]),
                    "value": sailkapena['stats'][team]['rowers']['bajak']
                } for sailkapena in sailkapenak if team in sailkapena['stats']
                           and 'rowers' in sailkapena['stats'][team]]
            }
            result.append(altak)
            result.append(bajak)
        return result


@api.route('/', strict_slashes=False)
class Estatistikak(Resource):
    @api.expect(estatistikak_parser, validate=True)
    def get(self):
        result = []
        args = estatistikak_parser.parse_args()
        year = args.get('year')
        team = args.get('team')
        league = args.get('league')
        category = args.get('category')
        stat_type = args.get('stat')
        logging.info(f'Stat {stat_type}*{team}*')
        if stat_type == 'cumulative':
            result = EstatistikakLogic.get_culumative_stats(league, year, team, category)
        elif stat_type == 'points':
            if team:
                result = EstatistikakLogic.get_points(league, team)
            else:
                if not league or not year:
                    return {"message": "You need to specify year and league"}, 400
                result = EstatistikakLogic.get_points_per_race(league, year, category)
        elif stat_type == 'rank':
            if team and not league:
                return {"message": "You need to specify a league"}, 400
            if not team and (not league or not year):
                return {"message": "You need to specify year and league"}, 400
            result = EstatistikakLogic.get_rank(league, year, team, category)
        elif stat_type == 'ages':
            if team and not league:
                return {"message": "You need to specify a league"}, 400
            if not team and (not league or not year):
                return {"message": "You need to specify year and league"}, 400
            result = EstatistikakLogic.get_ages(league, year, team)
        elif stat_type == 'incorporations':
            result = EstatistikakLogic.get_incorporations(league, year, team)
        return result
