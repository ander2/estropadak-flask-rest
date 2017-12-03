import couchdb
import sys
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

        # parser = reqparse.RequestParser()
        # parser.add_argument('startdate', type=str)
        # parser.add_argument('enddate', type=str)
        # args = parser.parse_args()
        start = [league, yearz]
        end = [league, fyearz]
        print("{} {}".format(start, end))
        # if 'startdate' in args:
        #     start = [league, args['startdate']]
        # if 'enddate' in args:
        #     end= [league, args['enddate']]
        print("{} {}".format(start, end))
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

