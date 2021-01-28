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
        except TypeError:
            logging.error("Not found", exc_info=1)
            estropada = None
        except KeyError:
            logging.error("Not found", exc_info=1)
            estropada = None
        return estropada

    @staticmethod
    def get_estropadak_by_league_year(league, year, page=0, count=app.config.PAGE_SIZE):
        logging.info("League:%s and year: %s", league, year)
        start = []
        end = []
        if league:
            league = league.upper()
            if league.lower() == 'euskotren':
                league = league.lower()
            start.append(league)
            end.append(league)

        if year:
            yearz = "{}".format(year)
            fyearz = "{}z".format(year)
            start.append(yearz)
            end.append(fyearz)
        else:
            end = ["{}z".format(league)]

        try:
            estropadak = db.get_view_result("estropadak", "all",
                                            raw_result=True,
                                            startkey=start,
                                            endkey=end,
                                            include_docs=True,
                                            reduce=False,
                                            skip=count*page,
                                            limit=count)
            result = []
            for row in estropadak['rows']:
                puntuagarria = True
                estropada = estropadak_transform(row['doc'])
                result.append(estropada.format_for_json(estropada))
            return result
        except KeyError:
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
            args['year'],
            args['page'],
            args['count'])
        return estropadak


@api.route('/<string:estropada_id>')
class Estropada(Resource):
    def get(self, estropada_id):
        estropada = EstropadakDAO.get_estropada_by_id(estropada_id)
        if estropada is None:
            return "Estropada not found", 404
        else:
            return estropada.format_for_json(estropada)
