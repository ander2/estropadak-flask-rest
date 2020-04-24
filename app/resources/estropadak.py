import couchdb
import logging

from flask_restful import Resource, reqparse, inputs
from app.db_connection import db
from .utils import estropadak_transform


class EstropadakDAO:
    @staticmethod
    def get_estropada_by_id(id):
        try:
            estropada = estropadak_transform(db[id])
        except TypeError as error:
            logging.error("Not found", error)
            estropada = None
        except couchdb.http.ResourceNotFound as error:
            logging.error("Not found", error)
            estropada = None
        return estropada

    @staticmethod
    def get_estropadak_by_league_year(league, year):
        logging.info("League:%s and year: %s", league, year)
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        start = [league]
        end = [league]

        if year is not None:
            yearz = "{}".format(year)
            fyearz = "{}z".format(year)
            start.append(yearz)
            end.append(fyearz)
        else:
            end = ["{}z".format(league)]

        try:
            estropadak = db.view("estropadak/all",
                                 None,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=False,
                                 reduce=False)
            result = []
            for estropada in estropadak.rows:
                puntuagarria = True
                if db[estropada.id].get('puntuagarria', True) is False:
                    puntuagarria = False
                result.append({
                    'id': estropada.id,
                    'data': estropada.key[1],
                    'izena': estropada.key[2],
                    'puntuagarria': puntuagarria
                })
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404


class Years(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('historial', required=False, default=False)
        args = parser.parse_args()
        doc = db['years']
        del doc['_id']
        del doc['_rev']
        if args['historial'] and inputs.boolean(args['historial']):
            for k, v in doc.items():
                doc[k] = [year for year in v if year > 2009]
        return doc


class ActiveYear(Resource):
    def get(self):
        doc = db['active_year']
        return doc['year']


class Estropadak(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('league', type=str)
        parser.add_argument('year', type=str, default=None)
        args = parser.parse_args()
        estropadak = EstropadakDAO.get_estropadak_by_league_year(
            args['league'],
            args['year'])
        return estropadak


class Estropada(Resource):
    def get(self, estropada_id):
        estropada = EstropadakDAO.get_estropada_by_id(estropada_id)
        if estropada is None:
            return {}
        else:
            return estropada.format_for_json(estropada)
