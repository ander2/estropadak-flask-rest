import app.config
import logging

from app.db_connection import db
from .utils import estropadak_transform
from .taldeak import TaldeakDAO
from flask_restx import Namespace, Resource, reqparse

api = Namespace('emaitzak', description='')


class EmaitzakDAO:

    @staticmethod
    def get_estropada_by_id(id):
        try:
            estropada = estropadak_transform(db[id])
        except TypeError:
            logging.debug("Not found", exc_info=1)
            estropada = None
        except KeyError:
            logging.debug("Not found", exc_info=1)
            estropada = None
        return estropada

    @staticmethod
    def get_estropadak_by_league_year(league, year, team=None):
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        if year:
            yearz = "{}".format(year)
            fyearz = "{}z".format(year)
            start = [league, yearz]
            end = [league, fyearz]
        else:
            start = [league]
            end = [league + 'z']

        estropadak = db.get_view_result("estropadak", "all",
                                startkey=start,
                                endkey=end,
                                include_docs=True,
                                reduce=False)
        result = []
        alt_names = []
        if team:
            teams = TaldeakDAO.get_taldeak(league, year)
            team_names = [t for t in teams if t['name'] == team]
            if len(team_names) > 0:
                alt_names = team_names[0]['alt_names']
        for estropada in estropadak:
            estropada = estropadak_transform(estropada)
            team_estropada = estropada
            if len(alt_names) > 0 and hasattr(estropada, 'sailkapena'):
                team_estropada.sailkapena = [
                    talde_emaitza for talde_emaitza in estropada.sailkapena
                    if talde_emaitza.talde_izena in alt_names
                ]
            if hasattr(estropada, 'sailkapena'):
                result.append(team_estropada)
        return result

    @staticmethod
    def get_estropadak_by_team(team, league_id):
        start = [team]
        if league_id:
            start.append(league_id)
        end = ["{}z".format(team)]
        if league_id:
            end.append(league_id)
        try:
            estropadak = db.view("estropadak/by_team",
                                 estropadak_transform,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=True,
                                 reduce=False)
            result = []
            for estropada in estropadak.rows:
                result.append(estropada)
            return result
        except KeyError:
            return {'error': 'Estropadak not found'}, 404


@api.route('/', strict_slashes=False)
class Emaitzak(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('league', type=str, choices=app.config.LEAGUES, case_sensitive=False, help="League abbreviation", required=True)
        parser.add_argument('year', type=int, help="Year")
        parser.add_argument('team', type=str, help="Team name")
        args = parser.parse_args()
        try:
            estropadak = EmaitzakDAO.get_estropadak_by_league_year(
                args['league'],
                args['year'],
                args['team'])
            return [estropada.format_for_json(estropada)
                    for estropada in estropadak]
        except Exception:
            return {'error': 'Estropadak not found'}, 404