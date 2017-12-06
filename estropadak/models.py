import couchdb
import sys
import logging
from flask_restful import Resource, reqparse

couch_server = couchdb.Server()
db = couch_server['estropadak']


class Years(Resource):
    def get(self):
        doc = db['years']
        del doc['_id']
        del doc['_rev']
        return doc


class Estropadak(Resource):
    def get(self, league_id, year):
        league = league_id.upper()
        yearz = "{}".format(year)
        fyear = year + "z"
        fyearz = "{}".format(fyear)

        start = [league, yearz]
        end = [league, fyearz]
        try:
            estropadak = db.view("estropadak/all",
                                 None,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=True,
                                 reduce=False)
            result = estropadak.rows
        except:
            result = []
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
        logging.info(key)
        doc = db[key]
        if team:
            return doc['stats'][team]
        return doc['stats']
