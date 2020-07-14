import couchdb
import logging
import app.config

from flask_restx import Namespace, Resource
from app.db_connection import db
from .utils import estropadak_transform, league_year_parser

api = Namespace('estropadak', description='')


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


@api.route('/', strict_slashes=False)
class Estropadak(Resource):
    @api.expect(league_year_parser, validate=True)
    def get(self):
        args = league_year_parser.parse_args()
        if args.get('year') and args.get('year') < app.config.MIN_YEAR:
            return "Year not found", 400
        estropadak = EstropadakDAO.get_estropadak_by_league_year(
            args['league'],
            args['year'])
        return estropadak


@api.route('/<string:estropada_id>')
class Estropada(Resource):
    def get(self, estropada_id):
        estropada = EstropadakDAO.get_estropada_by_id(estropada_id)
        if estropada is None:
            return "Estropada not found", 404
        else:
            return estropada.format_for_json(estropada)
