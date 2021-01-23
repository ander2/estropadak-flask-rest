from json.decoder import JSONDecodeError
import app.config
import logging
import json

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
    def get_emaitzak_by_league_year(league, year, team=None):
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        if year:
            start = [league, team, year]
            end = [league, team, year + 1]
        else:
            start = [league, team]
            end = [league, team + 'z']

        emaitzak = db.get_view_result("emaitzak", "by_team",
                                startkey=start,
                                endkey=end,
                                include_docs=False,
                                reduce=False)
        result = []
        for emaitza in emaitzak:
            result.append(db[emaitza['id']])
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
    
    @staticmethod
    def get_emaitzak(criteria: dict):
        logging.info(criteria)
        emaitzak = db.get_query_result(criteria)
        result = []
        for emaitza in emaitzak:
            result.append(emaitza)

        return result


@api.route('/', strict_slashes=False)
class Emaitzak(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('criteria', type=str, help="Search criteria")
        args = parser.parse_args()
        try:
            criteria = json.loads(args['criteria'])
        except JSONDecodeError:
            return {"message": "Bad criteria, please check the query"}, 400
        try:
            emaitzak = EmaitzakDAO.get_emaitzak(criteria)
            return emaitzak
        except Exception:
            logging.info("Error", exc_info=1)
            return {'error': 'Estropadak not found'}, 404