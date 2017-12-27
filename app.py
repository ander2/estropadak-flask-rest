from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from resources.estropadak import Estropadak, Estropada, Sailkapena, Years

app = Flask(__name__)

def routes(app):
    api = Api(app)
    api.add_resource(Years, '/years')
    api.add_resource(Sailkapena, '/sailkapena/<league_id>/<year>', '/sailkapena/<league_id>/<year>/<team>')
    api.add_resource(Estropadak, '/estropadak/<league_id>/<year>')
    api.add_resource(Estropada, '/estropada/<estropada_id>')

routes(app)
cors = CORS(app, resources={r"/estropada[k]?/*": {"origins": "*"}})


if __name__ == '__main__':
    app.run(debug=True)
