import logging
import json

from json.decoder import JSONDecodeError
from flask_restx import Namespace, Resource, reqparse, fields
from flask_jwt import jwt_required
from app.config import LEAGUES, PAGE_SIZE
from ..dao.emaitzak_dao import EmaitzakDAO
from .taldeak import TaldeakDAO


api = Namespace('emaitzak', description='')
emaitza_model = api.model('Emaitza', {
    'id': fields.String(required=False, attribute="_id"),
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
    'liga': fields.String(required=True, enum=LEAGUES),
    'estropada_id': fields.String(required=True)
})

emaitzak_list_model = api.model('Emaitza listing model', {
    'docs': fields.List(fields.Nested(emaitza_model)),
    'total': fields.Integer(example=1)
})


class EmaitzakLogic:
    @staticmethod
    def update_emaitza(emaitza_id, emaitza):
        emaitza['type'] = 'emaitza'
        talde_izen_normalizatua = TaldeakDAO.get_talde_izen_normalizatua(emaitza['talde_izena'])
        emaitza['talde_izen_normalizatua'] = talde_izen_normalizatua
        return EmaitzakDAO.update_emaitza_into_db(emaitza_id, emaitza)

    @staticmethod
    def create_emaitzak_from_estropada(estropada):
        for emaitza in estropada['sailkapena']:
            emaitza['type'] = 'emaitza'
            emaitza['estropada_data'] = estropada['data']
            emaitza['estropada_izena'] = estropada['izena']
            emaitza['estropada_id'] = estropada['_id']
            emaitza['liga'] = estropada['liga']
            talde_izen_normalizatua = TaldeakDAO.get_talde_izen_normalizatua(emaitza['talde_izena'])
            emaitza['talde_izen_normalizatua'] = talde_izen_normalizatua
            # try:
            #     emaitza['estropada_data'] = datetime.datetime.fromisoformat(estropada['data'])
            # except ValueError:
            #     emaitza['estropada_data'] = datetime.datetime.strptime(estropada['data'], '%Y-%m-%d %H:%M')
            EmaitzakDAO.insert_emaitza_into_db(emaitza)
        return True


@api.route('/', strict_slashes=False)
class Emaitzak(Resource):
    @api.marshal_with(emaitzak_list_model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('criteria', type=str, help="Search criteria")
        parser.add_argument('page', type=int, help="Page number", default=0)
        parser.add_argument('count', type=int, help="Elements per page", default=PAGE_SIZE)
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

    @jwt_required()
    @api.expect(emaitza_model, validate=True)
    def put(self, emaitza_id):

        data = api.payload

        emaitza = EmaitzakLogic.update_emaitza(emaitza_id, data)

        if emaitza:
            return emaitza
        else:
            return {}, 404

    @jwt_required()
    def delete(self, emaitza_id):

        emaitza = EmaitzakDAO.delete_emaitza_from_db(emaitza_id)

        if emaitza:
            return {}, 200
        else:
            return {"msg": "Cannot delete document"}, 401
