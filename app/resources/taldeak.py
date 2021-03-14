import logging
from app.db_connection import db
from flask_restx import Namespace, Resource
from .utils import required_league_year_parser
from .estropadak import EstropadakDAO

api = Namespace('taldeak', description='')


class PlantilaDAO:

    @staticmethod
    def get_plantila(team, league, year):
        try:
            id = f'team_{league}_{year}_{team}'
            taldea = db[id]
            talde_izenak = db['talde_izenak']
            talde_izenak = {k.lower(): v for k, v in talde_izenak.items()}
            _rowers = []
            for i, rower in enumerate(taldea['rowers']):
                historial = []
                for h in rower['historial']:
                    t = list(h.items())
                    try:
                        normalized_name = talde_izenak[t[0][1].lower()]
                    except KeyError:
                        normalized_name = t[0][1]
                    historial.append({'name': normalized_name, 'year': t[0][0]})
                rower['historial'] = historial
                rower['name'] = ' '.join(rower['name'].split(' ')[:-1]).title()
                rower['index'] = i
                _rowers.append(rower)
            taldea['rowers'] = _rowers

        except TypeError as error:
            logging.info("Not found", exc_info=1)
            taldea = None
        except KeyError as error:
            logging.info("Not found", exc_info=1)
            taldea = None
        return taldea


class TaldeakDAO:

    @staticmethod
    def get_taldea_by_id(id):
        try:
            taldea = db[id]
        except TypeError as error:
            logging.info("Not found", exc_info=1)
            taldea = None
        except KeyError as error:
            logging.info("Not found", exc_info=1)
            taldea = None
        return taldea

    @staticmethod
    def get_taldeak(league, year=None):
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()

        taldeak = []
        try:
            if year is not None:
                resume = db[f'rank_{league}_{year}']
                all_teams = db['talde_izenak']
                for taldea in resume['stats'].keys():
                    alt_names = [alt for alt, name in all_teams.items() if name == taldea]
                    taldeak.append({'name': taldea, 'alt_names': alt_names})
            else:
                league = league.lower()
                resume = db[f'taldeak_{league}']
                all_teams = db['talde_izenak']
                for taldea in resume['taldeak']:
                    alt_names = [alt for alt, name in all_teams.items() if name == taldea]
                    taldeak.append({'name': taldea, 'alt_names': alt_names})
        except KeyError as error:
            logging.info("Not found", exc_info=1)
        return taldeak

    @staticmethod
    def get_talde_izen_normalizatua(taldea):
        talde_izenak = db['talde_izenak']
        try:
            talde_izena = talde_izenak[taldea]
        except KeyError:
            talde_izena = talde_izenak[taldea.title()]
        return talde_izena


@api.route('/', strict_slashes=False)
class Taldeak(Resource):
    @api.expect(required_league_year_parser, validate=True)
    def get(self):
        args = required_league_year_parser.parse_args()
        teams = []
        league = args.get('league')
        year = args.get('year')
        teams = TaldeakDAO.get_taldeak(league, year)
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
        team = PlantilaDAO.get_plantila(team, league, args['year'])
        if team is None:
            return {'message': 'Team not found'}, 404
        return team


class TaldeakByName(Resource):
    def get(self, talde_izena, league_id=None):
        all_names = db['talde_izenak']
        normalized_name = all_names[talde_izena]
        names = [key for key, val in all_names.items() if val == normalized_name]
        result = []
        for name in names:
            estropadak = EstropadakDAO.get_estropadak_by_team(name, league_id)
            result.extend(estropadak)
        return [res.format_for_json(res) for res in result]
