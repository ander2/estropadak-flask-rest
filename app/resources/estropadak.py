import couchdb
import sys
import logging
from flask_restful import Resource, reqparse
from app.config import config
import time

db = None
while db is None:
    try:
        couch_server = couchdb.Server(config['COUCHDB'])
        db = couch_server['estropadak']
    except:
        pass

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
        league = league_id.upper()
        if league_id.lower() == 'euskotren':
            league = league_id.lower()
        yearz = "{}".format(year)
        fyear = year + "z"
        fyearz = "{}".format(fyear)

        start = [league, yearz]
        end = [league, fyearz]
        try:
            estropadak = db.view("estropadak/all",
                                 normalize_id,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=True,
                                 reduce=False)
            result = [estropada['doc'] for estropada in estropadak.rows]
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404
        return result


class Estropada(Resource):
    def get(self, estropada_id):
        try:
            doc = db[estropada_id]
        except:
            doc = {}
        return doc

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
