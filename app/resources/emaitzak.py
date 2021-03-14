from json.decoder import JSONDecodeError
import app.config
import logging
import json
import datetime

from app.db_connection import db
from .utils import estropadak_transform
from .taldeak import TaldeakDAO
from flask_restx import Namespace, Resource, reqparse, fields
from flask_jwt import jwt_required

api = Namespace('emaitzak', description='')
emaitza_model = api.model('Emaitza', {
    'talde_izena': fields.String(required=True),
    'ziabogak': fields.List(fields.String, required=True),
    'kalea': fields.Integer(required=True),
    'tanda': fields.Integer(required=True),
    'tanda_postua': fields.Integer(required=True),
    'denbora': fields.String(),
    'posizioa': fields.Integer(),
    'puntuazioa': fields.Integer(),
    'kategoria': fields.String(),
    'estropada_izena': fields.String(required=True, min_length=8),
    'estropada_data': fields.DateTime(required=True),
    'talde_izen_normalizatua': fields.String(),
    'liga': fields.String(required=True, enum=app.config.LEAGUES),
    'estropada_id': fields.String(required=True)
})


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
    def get_emaitza_by_id(id):
        try:
            emaitza = db[id]
        except KeyError:
            emaitza = None
        return emaitza

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
    def get_emaitzak(criteria: dict, page: int, count: int):
        start = page * count
        end = start + count
        docs = []
        total = 0
        emaitzak = db.get_query_result(criteria)
        try:
            for emaitza in emaitzak:
                total = total + 1 
            emaitzak = db.get_query_result(criteria)
            docs = emaitzak[start:end]
        except IndexError:
            return {'error': 'Bad pagination'}, 400
        return (docs, total,)

    def insert_emaitza_into_db(emaitza):
        data = datetime.datetime.strptime(emaitza['estropada_data'], '%Y-%m-%d %H:%M')
        izena = emaitza['talde_izen_normalizatua'].replace(' ', '-')
        emaitza['_id'] = f'{data.strftime("%Y-%m-%d")}_{emaitza["liga"]}_{izena}'

        document = db.create_document(emaitza)
        return document.exists()


@api.route('/', strict_slashes=False)
class Emaitzak(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('criteria', type=str, help="Search criteria")
        parser.add_argument('page', type=int, help="Page number", default=0)
        parser.add_argument('count', type=int, help="Elements per page", default=app.config.PAGE_SIZE)
        args = parser.parse_args()
        try:
            criteria = json.loads(args['criteria'])
        except JSONDecodeError:
            return {"message": "Bad criteria, please check the query"}, 400
        try:
            docs, total = EmaitzakDAO.get_emaitzak(criteria, args['page'], args['count'])
            return {"docs": docs, "total": total}
        except Exception:
            logging.info("Error", exc_info=1)
            return {'error': 'Estropadak not found'}, 404

    @jwt_required()
    @api.expect(emaitza_model, validate=True)
    def post(self):
        emaitza = api.payload
        doc_created = EmaitzakDAO.insert_emaitza_into_db(emaitza)
        if doc_created:
            return {}, 201  # , "Estropada created"
        else:
            return {}, 400  # , "Cannot create estropada"


@api.route('/<string:emaitza_id>', strict_slashes=False)
class Emaitza(Resource):

    def get(self, emaitza_id):

        emaitza = EmaitzakDAO.get_emaitza_by_id(emaitza_id)
        if emaitza:
            return emaitza
        else:
            return {}, 404

