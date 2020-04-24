import couchdb
import logging
import time
from flask_restful import Resource, reqparse, inputs
from estropadakparser.estropada.estropada import Estropada as EstropadaModel, TaldeEmaitza
from app.resources.taldeak import TaldeakDAO
from app.db_connection import db

def estropadak_transform(row):
    if 'doc' in row:
        document = row['doc']
    else:
        document = row
    row = normalize_id(row)
    izena = document['izena']
    if 'sailkapena' not in document:
        document['sailkapena'] = []
    sailkapena = document['sailkapena']
    del(document['izena'])
    del(document['sailkapena'])
    estropada = EstropadaModel(izena, **document)
    logging.info(estropada)
    for sailk in sailkapena:
        estropada.taldeak_add(TaldeEmaitza(**sailk))
    return estropada

class EstropadakDAO:
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
                    'data':estropada.key[1],
                    'izena': estropada.key[2],
                    'puntuagarria': puntuagarria
                })
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404

class EmaitzakDAO:

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
    def get_estropadak_by_league_year(league, year, team=None):
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        yearz = "{}".format(year)
        fyearz = "{}z".format(year)
        start = [league, yearz]
        end = [league, fyearz]
        try:
            estropadak = db.view("estropadak/all",
                                 estropadak_transform,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=True,
                                 reduce=False)
            result = []
            alt_names = []
            if team:
                teams = TaldeakDAO.get_taldeak(league, year)
                team_names = [t for t in teams if t['name'] == team]
                if len(team_names) > 0:
                    alt_names = team_names[0]['alt_names']
            for estropada in estropadak.rows:
                team_estropada = estropada
                if len(alt_names) > 0 and hasattr(estropada, 'sailkapena'):
                    team_estropada.sailkapena = [talde_emaitza for talde_emaitza in estropada.sailkapena if talde_emaitza.talde_izena in alt_names]
                if hasattr(estropada, 'sailkapena'):
                    result.append(team_estropada)
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404

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
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404


def normalize_id(row):
    if 'doc' in row:
        row['doc']['id'] = row['doc']['_id']
        del row['doc']['_id']
        del row['doc']['_rev']
    else:
        row['id'] = row['_id']
        del row['_id']
        del row['_rev']
    return row

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
        estropadak = EstropadakDAO.get_estropadak_by_league_year(args['league'], args['year'])
        return estropadak

class Emaitzak(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('league', type=str)
        parser.add_argument('year', type=str)
        parser.add_argument('team', type=str)
        args = parser.parse_args()
        estropadak = EmaitzakDAO.get_estropadak_by_league_year(args['league'], args['year'], args['team'])
        return [estropada.format_for_json(estropada) for estropada in estropadak]

class Estropada(Resource):
    def get(self, estropada_id):
        estropada = EmaitzakDAO.get_estropada_by_id(estropada_id)
        if estropada is None:
            return {}
        else:
            return estropada.format_for_json(estropada)
