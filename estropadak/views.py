from flask_restful import Api
from .models import Estropadak, Estropada, Years

def routes(app):
    api = Api(app)
    api.add_resource(Years, '/years')
    api.add_resource(Estropadak, '/estropadak/<league_id>/<year>')
    api.add_resource(Estropada, '/estropada/<estropada_id>')