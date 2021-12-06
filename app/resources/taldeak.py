import logging
from app.db_connection import get_db_connection
from flask_restx import Namespace, Resource, fields
from .utils import required_league_year_parser

api = Namespace('taldeak', description='')

taldeak_model = api.model('Taldea', {
    'name': fields.String(required=True),
    'alt_names': fields.List(fields.String, required=False),
    'short': fields.String(required=False),
})


class PlantilaDAO:

    @staticmethod
    def get_plantila(team, league, year):
        with get_db_connection() as database:
            try:
                id = f'team_{league}_{year}_{team}'
                taldea = database[id]
                talde_izenak = database['talde_izenak']
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

            except TypeError:
                logging.info("Not found", exc_info=1)
                taldea = None
            except KeyError:
                logging.info("Not found", exc_info=1)
                taldea = None
            return taldea


class TaldeakDAO:

    @staticmethod
    def get_taldea_by_id(id):
        with get_db_connection() as database:
            try:
                taldea = database[id]
            except TypeError:
                logging.info("Not found", exc_info=1)
                taldea = None
            except KeyError:
                logging.info("Not found", exc_info=1)
                taldea = None
            return taldea

    @staticmethod
    def get_taldeak(league, year=None):
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()

        taldeak = []
        with get_db_connection() as database:
            try:
                all_teams = database['talde_izenak2']
                if year is not None:
                    resume = database[f'rank_{league}_{year}']
                    for taldea in resume['stats'].keys():
                        taldeak.append({
                            "name": taldea,
                            "alt_names": all_teams[taldea].get('alt_names'),
                            "short": all_teams[taldea].get('acronym')
                        })
                else:
                    league = league.lower()
                    resume = database[f'taldeak_{league}']
                    for taldea in resume['taldeak']:
                        taldeak.append({
                            "name": taldea,
                            "alt_names": all_teams[taldea].get('alt_names'),
                            "short": all_teams[taldea].get('acronym')
                        })
            except KeyError:
                logging.info("Not found", exc_info=1)
            return taldeak

    @staticmethod
    def get_talde_izen_normalizatua(taldea):
        with get_db_connection() as database:
            talde_izenak = database['talde_izenak']
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
