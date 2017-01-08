from flask import Flask
from flask_restful import Resource, Api
from flask.ext.cors import CORS
import couchdb

app = Flask(__name__)
cors = CORS(app, resources={r"/estropada[k]?/*": {"origins": "*"}})
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

api.add_resource(Years, '/years')
api.add_resource(Estropadak, '/estropadak/<league_id>/<year>')
api.add_resource(Estropada, '/estropada/<estropada_id>')

if __name__ == '__main__':
    app.run(debug=True)
