import logging
import app.config
import datetime

from flask_restx import Namespace, Resource, fields
from flask_jwt import jwt_required
from app.db_connection import db
from .utils import estropadak_transform, league_year_parser


api = Namespace('estropadak', description='')

estropada_model = api.model('Estropada', {
    'izena': fields.String,
    'data': fields.DateTime,
    'liga': fields.String,
    'sailkapena': fields.Arbitrary
})


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

    @staticmethod
    def insert_estropada_into_db(estropada):
        data = datetime.datetime.strptime(estropada['data'], '%Y-%m-%d %H:%M')
        izena = estropada['izena'].replace(' ', '-')
        estropada['_id'] = f'{data.strftime("%Y-%m-%d")}_{estropada["liga"]}_{izena}'

        logging.info(estropada)
        document = db.create_document(estropada)
        return document.exists()

    @staticmethod
    def update_estropada_into_db(estropada_id, estropada):
        doc = db[estropada_id]
        doc['izena'] = estropada['izena']
        doc['data'] = estropada['data']
        doc['liga'] = estropada['liga']
        doc['sailkapena'] = estropada['sailkapena']
        doc.save()

    @staticmethod
    def delete_estropada_from_db(estropada_id):
        doc = db[estropada_id]
        if doc.exists():
            doc.fetch()
            doc.delete()


class EstropadakLogic():

    @staticmethod
    def create_estropada(estropada):
        if estropada.get('type', 'estropada') != 'estropada':
            estropada['type'] = 'estropada'
        if estropada.get('sailkapena', []):
            # todo implement EmaitzaLogic.create_emaitza
            pass
        return EstropadakDAO.insert_estropada_into_db(estropada)

    @staticmethod
    def update_estropada(estropada_id, estropada):
        if estropada.get('type', 'estropada') != 'estropada':
            estropada['type'] = 'estropada'
        if estropada.get('sailkapena', []):
            # todo implement EmaitzaLogic.create_emaitza
            pass
        return EstropadakDAO.update_estropada_into_db(estropada_id, estropada)

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

    @jwt_required()
    @api.expect(estropada_model)
    @api.response(201, 'Estropada created')
    @api.response(400, 'Validation Error')
    def post(self):
        data = api.payload
        doc_created = EstropadakLogic.create_estropada(data)
        if doc_created:
            return {}, 201 # , "Estropada created"
        else:
            return {}, 400 # , "Cannot create estropada"



@api.route('/<string:estropada_id>')
class Estropada(Resource):
    def get(self, estropada_id):
        estropada = EstropadakDAO.get_estropada_by_id(estropada_id)
        if estropada is None:
            return "Estropada not found", 404
        else:
            return estropada.format_for_json(estropada)

    @jwt_required()
    @api.expect(estropada_model)
    def put(self, estropada_id):
        data = api.payload
        EstropadakLogic.update_estropada(estropada_id, data)

    @jwt_required()
    def delete(self, estropada_id):
        EstropadakDAO.delete_estropada_from_db(estropada_id)
