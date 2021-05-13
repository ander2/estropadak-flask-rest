import logging

from attr import attributes

import app.config
import datetime

from flask_restx import Namespace, Resource, fields
from flask_jwt import jwt_required
from app.db_connection import get_db_connection
from .utils import league_year_parser


api = Namespace('estropadak', description='')

emaitza_model = api.model('Emaitza estropadan', {
    'talde_izena': fields.String(required=True),
    'ziabogak': fields.List(fields.String, required=True),
    'kalea': fields.Integer(required=True),
    'tanda': fields.Integer(required=True),
    'tanda_postua': fields.Integer(required=True),
    'denbora': fields.String(),
    'posizioa': fields.Integer(),
    'puntuazioa': fields.Integer(),
    'kategoria': fields.String(),
})

estropada_model = api.model('Estropada', {
    'id': fields.String(required=False, attribute="_id"),
    'izena': fields.String(required=True, min_length=4),
    'data': fields.DateTime(required=True),
    'lekua': fields.String(required=False),
    'liga': fields.String(required=True, enum=app.config.LEAGUES),
    'sailkapena': fields.List(fields.Nested(emaitza_model)),
    'urla': fields.String(min_length=8),
    'puntuagarria': fields.Boolean(required=False, default=True),
    'kategoriak': fields.List(fields.String(), required=False),
    'oharrak': fields.String(required=False)
})


class EstropadakDAO:
    @staticmethod
    def get_estropada_by_id(id):
        
        with get_db_connection() as database:
            try:
                estropada = database[id]
                estropada['data'] = estropada['data'].replace(' ', 'T')
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

        with get_db_connection() as database:
            try:
                estropadak = database.get_view_result("estropadak", "all",
                                                      raw_result=True,
                                                      startkey=start,
                                                      endkey=end,
                                                      include_docs=True,
                                                      reduce=False,
                                                      skip=count*page,
                                                      limit=count)
                result = []
                for row in estropadak['rows']:
                    estropada = row['doc']
                    estropada['data'] = estropada['data'].replace(' ', 'T')
                    result.append(estropada)
                return result
            except KeyError:
                return {'error': 'Estropadak not found'}, 404

    @staticmethod
    def insert_estropada_into_db(estropada):
        data = datetime.datetime.strptime(estropada['data'], '%Y-%m-%d %H:%M')
        izena = estropada['izena'].replace(' ', '-')
        estropada['_id'] = f'{data.strftime("%Y-%m-%d")}_{estropada["liga"]}_{izena}'

        logging.info(estropada)
        with get_db_connection() as database:
            document = database.create_document(estropada)
            return document.exists()

    @staticmethod
    def update_estropada_into_db(estropada_id, estropada):
        with get_db_connection() as database:
            doc = database[estropada_id]
            doc['izena'] = estropada['izena']
            doc['data'] = estropada['data']
            doc['liga'] = estropada['liga']
            doc['sailkapena'] = estropada['sailkapena']
            doc['type'] = estropada['type']
            doc.save()

    @staticmethod
    def delete_estropada_from_db(estropada_id):
        with get_db_connection() as database:
            doc = database[estropada_id]
            if doc.exists():
                doc.fetch()
                doc.delete()


class EstropadakLogic():

    @staticmethod
    def create_estropada(estropada):
        if estropada.get('type', None) != 'estropada':
            estropada['type'] = 'estropada'
        if estropada.get('sailkapena', []):
            # todo implement EmaitzaLogic.create_emaitza
            pass
        return EstropadakDAO.insert_estropada_into_db(estropada)

    @staticmethod
    def update_estropada(estropada_id, estropada):
        if estropada.get('type', None) != 'estropada':
            estropada['type'] = 'estropada'
        if estropada.get('sailkapena', []):
            # todo implement EmaitzaLogic.create_emaitza
            pass
        return EstropadakDAO.update_estropada_into_db(estropada_id, estropada)


@api.route('/', strict_slashes=False)
class Estropadak(Resource):
    @api.marshal_with(estropada_model)
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

    @jwt_required()
    @api.expect(estropada_model, validate=True)
    @api.response(201, 'Estropada created')
    @api.response(400, 'Validation Error')
    def post(self):
        data = api.payload
        doc_created = EstropadakLogic.create_estropada(data)
        if doc_created:
            return {}, 201  # , "Estropada created"
        else:
            return {}, 400  # , "Cannot create estropada"


@api.route('/<string:estropada_id>')
class Estropada(Resource):
    @api.marshal_with(estropada_model)
    def get(self, estropada_id):
        estropada = EstropadakDAO.get_estropada_by_id(estropada_id)
        if estropada is None:
            return "Estropada not found", 404
        else:
            return estropada

    @jwt_required()
    @api.expect(estropada_model, validate=True)
    def put(self, estropada_id):
        data = api.payload
        EstropadakLogic.update_estropada(estropada_id, data)

    @jwt_required()
    def delete(self, estropada_id):
        EstropadakDAO.delete_estropada_from_db(estropada_id)
