from flask import Flask
from flask_restful import Resource, Api
import couchdb

app = Flask(__name__)
api = Api(app)
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
        try:
            estropadak = db.view("estropadak/all", startkey=[league, yearz],
                    endkey=[league, fyearz], include_docs=True)
            result = estropadak.rows
        except(e):
            result = []
        return result

api.add_resource(Years, '/years')
api.add_resource(Estropadak, '/estropadak/<league_id>/<year>')

if __name__ == '__main__':
    app.run(debug=True)
