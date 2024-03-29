import logging
import datetime

from flask_restx import Namespace, Resource, fields, abort
from flask_jwt import jwt_required
from ..dao.estropadak_dao import EstropadakDAO
from .common.parsers import league_year_parser
from ..config import LEAGUES 
from .emaitzak import EmaitzakLogic
from .urteak import YearsDAO


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
    'liga': fields.String(required=True, enum=LEAGUES),
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

estropadak_list_model = api.model('Estropada listing model', {
    'docs': fields.List(fields.Nested(estropada_model)),
    'total': fields.Integer(example=1)
})


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
                        delta = datetime.timedelta(
                            minutes=denb2.minute,
                            seconds=denb2.second,
                            microseconds=denb2.microsecond)
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
                    estropada['bi_eguneko_sailkapena'] = sorted(
                        estropada['bi_eguneko_sailkapena'],
                        key=lambda x: x['denbora_batura'])
                    for ind, item in enumerate(estropada['bi_eguneko_sailkapena']):
                        item['posizioa'] = ind + 1
        return estropada

    def _validate_league_year(league: str, year: int) -> bool:
        if not league and not year:
            return True
        all_years = YearsDAO.get_years_from_db()
        if league in all_years:
            return year in all_years[league]
        else:
            return False


@api.route('/', strict_slashes=False)
class Estropadak(Resource):
    @api.expect(league_year_parser, validate=True)
    @api.response(400, 'Validation error')
    @api.marshal_with(estropadak_list_model, skip_none=True, code=200, description='Success')
    def get(self):
        args = league_year_parser.parse_args()
        estropadak = EstropadakDAO.get_estropadak(
            league=args['league'],
            year=args['year'],
            page=args['page'],
            count=args['count'])
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
