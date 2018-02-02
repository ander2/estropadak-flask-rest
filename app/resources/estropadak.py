import couchdb
import sys
import logging
from flask_restful import Resource, reqparse
from app.config import config
from estropadakparser.estropada.estropada import Estropada as EstropadaModel
import time

db = None
while db is None:
    try:
        couch_server = couchdb.Server(config['COUCHDB'])
        db = couch_server['estropadak']
    except:
        pass

def estropadak_transform(row):
    if 'doc' in row:
        document = row['doc']
    else:
        document = row
    print("{:=^30}".format(document['izena']))
    izena = document['izena']
    sailkapena = document['sailkapena']
    del(document['izena'])
    del(document['sailkapena'])
    estropada = EstropadaModel(izena, **document)
    for sailk in sailkapena:
        estropada.taldeak_add(sailk)
    return estropada


class EstropadakDAO:

    def get_estropada_by_id(id):
        try:
            # estropada = db[id]
            # izena = estropada['izena']
            # del estropada['izena']
            estropada = estropadak_transform(db[id])
        except TypeError as error:
            print("Type error:", error)
            estropada = None
        except couchdb.http.ResourceNotFound as error:
            print("Not found:", error)
            estropada = None
        return estropada

    def get_estropadak_by_league_year(league, year):
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
            for estropada in estropadak.rows:
                print(estropada.lekua)
                result.append(estropada)
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404


def normalize_id(row):
    row['doc']['id'] = row['doc']['_id']
    del row['doc']['_id']
    del row['doc']['_rev']
    return row

class Years(Resource):
    def get(self):
        doc = db['years']
        del doc['_id']
        del doc['_rev']
        return doc

class ActiveYear(Resource):
    def get(self):
        doc = db['active_year']
        return doc['year']


class Estropadak(Resource):
    def get(self, league_id, year):
        estropadak = EstropadakDAO.get_estropadak_by_league_year(league_id, year)
        return [estropada.format_for_json(estropada) for estropada in estropadak]


class Estropada(Resource):
    def get(self, estropada_id):
        estropada = EstropadakDAO.get_estropada_by_id(estropada_id)
        if estropada is None:
            return {}
        else:
            return estropada.format_for_json(estropada)

class Sailkapena(Resource):
    def get(self, league_id, year, team=None):
        key = 'rank_{}_{}'.format(league_id.upper(), year)
        try:
            doc = db[key]
        except couchdb.http.ResourceNotFound:
            return {'error': 'Stats not found'}, 404
        result = doc['stats']
        if team:
            try:
                result = result[team]
            except KeyError:
                return {'error': 'Team not found'}, 404
        return result
