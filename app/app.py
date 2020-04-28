import logging
from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from app.resources.active_year import api as active_year_api
from app.resources.urteak import api as urteak_api
from app.resources.estropadak import api as estropadak_api
from app.resources.emaitzak import api as emaitzak_api
from app.resources.taldeak import api as taldeak_api
from app.resources.sailkapenak import api as sailkapenak_api
from app.resources.estatistikak import api as estatistikak_api


DEBUG = True
logging.basicConfig(level='INFO')

app = Flask(__name__)
api = Api(app, version='1.0', title='Estropadak API',
          description='Estropadak API')
if DEBUG:
    CORS(app)


api.add_namespace(active_year_api)
api.add_namespace(urteak_api)
api.add_namespace(sailkapenak_api, path='/sailkapenak')
api.add_namespace(estropadak_api, path='/estropadak')
api.add_namespace(emaitzak_api, path='/emaitzak')
api.add_namespace(taldeak_api, path='/taldeak')
api.add_namespace(estatistikak_api)

if __name__ == '__main__':
    api.init_app(app)
    app.run()
