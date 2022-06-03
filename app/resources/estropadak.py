import logging
import datetime
from sys import exc_info
import app.config

from flask_restx import Namespace, Resource, fields
from flask_jwt import jwt_required
from app.db_connection import get_db_connection
from .utils import league_year_parser
from .emaitzak import EmaitzakLogic


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

bi_eguneko_emaitza_model = api.model('Emaitza estropadan', {
    'lehen_jardunaldiko_denbora': fields.String(),
    'bigarren_jardunaldiko_denbora': fields.String(),
    'denbora_batura': fields.String(),
    'posizioa': fields.Integer(),
    'talde_izena': fields.String(required=True)
})

estropada_model = api.model('Estropada', {
    'id': fields.String(required=False, attribute="_id"),
    'izena': fields.String(required=True, min_length=4),
    'data': fields.DateTime(required=True),
    'lekua': fields.String(required=False),
    'liga': fields.String(required=True, enum=app.config.LEAGUES),
    'sailkapena': fields.List(fields.Nested(emaitza_model)),
    'bi_jardunaldiko_bandera': fields.Boolean(default=False),
    'jardunaldia': fields.Integer(),
    'bi_eguneko_sailkapena': fields.List(fields.Nested(bi_eguneko_emaitza_model)),
    'related_estropada': fields.String(),
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
                if estropada['liga'] == 'euskotren':
                    estropada['liga'] = estropada['liga'].upper()
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
                    if estropada['liga'] == 'euskotren':
                        estropada['liga'] = estropada['liga'].upper()
                    result.append(estropada)
                return result
            except KeyError:
                return {'error': 'Estropadak not found'}, 404

    @staticmethod
    def insert_estropada_into_db(estropada):
        if estropada['liga'] == 'EUSKOTREN':
            estropada['liga'] = estropada['liga'].lower()
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
            if doc['liga'] == 'EUSKOTREN':
                estropada['liga'] = estropada['liga'].lower()
            doc['lekua'] = estropada['lekua']
            doc['sailkapena'] = estropada['sailkapena']
            doc['type'] = estropada['type']
            if estropada.get('bi_jardunaldiko_bandera'):
                doc['bi_jardunaldiko_bandera'] = estropada['bi_jardunaldiko_bandera']
            if estropada.get('related_estropada'):
                doc['related_estropada'] = estropada['related_estropada']
            if estropada.get('jardunaldia'):
                doc['jardunaldia'] = estropada['jardunaldia']
            if len(estropada.get('kategoriak', [])):
                doc['kategoriak'] = estropada['kategoriak']
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
        data = None
        try:
            data = datetime.datetime.fromisoformat(estropada['data'])
            logging.info(data)
        except ValueError:
            data = datetime.datetime.strptime(estropada['data'], '%Y-%m-%d %H:%M')
            estropada['data'] = data.isoformat()

        izena = estropada['izena'].replace(' ', '-')

        if estropada["liga"] == 'EUSKOTREN':
            estropada["liga"] = 'euskotren'
        estropada['_id'] = f'{data.strftime("%Y-%m-%d")}_{estropada["liga"]}_{izena}'

        if estropada.get('type', None) != 'estropada':
            estropada['type'] = 'estropada'
        if estropada.get('sailkapena', []):
            EmaitzakLogic.create_emaitzak_from_estropada(estropada)

        return EstropadakDAO.insert_estropada_into_db(estropada)

    @staticmethod
    def update_estropada(estropada_id, estropada):
        if estropada.get('type', None) != 'estropada':
            estropada['type'] = 'estropada'
        if estropada["liga"] == 'EUSKOTREN':
            estropada["liga"] = 'euskotren'
        if estropada.get('sailkapena', []):
            # todo implement EmaitzaLogic.create_emaitza
            pass
        return EstropadakDAO.update_estropada_into_db(estropada_id, estropada)

    @staticmethod
    def get_estropada(estropada_id):
        estropada = EstropadakDAO.get_estropada_by_id(estropada_id)
        if estropada and estropada.get('bi_jardunaldiko_bandera'):
            estropada['bi_eguneko_sailkapena'] = []
            estropada_bi = EstropadakDAO.get_estropada_by_id(estropada['related_estropada'])
            if len(estropada.get('sailkapena', [])) > 0 and len(estropada_bi.get('sailkapena', [])) > 0:
                denborak_bat = {sailk['talde_izena']: sailk['denbora'] for sailk in estropada['sailkapena']}
                denborak_bi = {sailk['talde_izena']: sailk['denbora'] for sailk in estropada_bi['sailkapena']}
                for taldea, denbora in denborak_bat.items():
                    try:
                        denb1 = datetime.datetime.strptime(denbora, '%M:%S,%f')
                        denb2 = datetime.datetime.strptime(denborak_bi[taldea], '%M:%S,%f')
                        delta = datetime.timedelta(minutes=denb2.minute, seconds=denb2.second, microseconds=denb2.microsecond)
                        totala = denb1 + delta
                        totala_str = totala.strftime('%M:%S,%f')[:-4]
                    except ValueError:
                        if denbora.startswith('Exc') or denborak_bi[taldea].startswith('Exc'):
                            totala_str = 'Excl.'
                    estropada['bi_eguneko_sailkapena'].append({
                        'talde_izena': taldea,
                        'lehen_jardunaldiko_denbora': denbora,
                        'bigarren_jardunaldiko_denbora': denborak_bi[taldea],
                        'denbora_batura': totala_str,
                    })
                    estropada['bi_eguneko_sailkapena'] = sorted(estropada['bi_eguneko_sailkapena'], key=lambda x: x['denbora_batura'])
                    for ind, item in enumerate(estropada['bi_eguneko_sailkapena']):
                        item['posizioa'] = ind + 1
        return estropada


@api.route('/', strict_slashes=False)
class Estropadak(Resource):
    @api.marshal_with(estropada_model, skip_none=True)
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
        try:
            doc_created = EstropadakLogic.create_estropada(data)
            if doc_created:
                return {}, 201  # , "Estropada created"
            else:
                return {}, 400  # , "Cannot create estropada"
        except Exception as e:
            logging.error("Error while creating an estropada", exc_info=1)
            return str(e), 400


@api.route('/<string:estropada_id>')
class Estropada(Resource):
    @api.marshal_with(estropada_model, skip_none=True)
    def get(self, estropada_id):
        estropada = EstropadakLogic.get_estropada(estropada_id)
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
