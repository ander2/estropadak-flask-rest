import logging
from flask import Flask
from flask_restful import Api
from app.resources.estropadak import (ActiveYear,
                                      Estropadak,
                                      Estropada)
from app.resources import (
    Sailkapena, Emaitzak, Years, Taldeak, TaldeakByLeague, Plantilla
)


logging.basicConfig(level='INFO')

app = Flask(__name__)


def routes(app):
    api = Api(app)
    api.add_resource(Years, '/years')
    api.add_resource(ActiveYear, '/active_year')
    api.add_resource(Sailkapena, '/sailkapena')
    api.add_resource(Estropadak, '/estropadak')
    api.add_resource(Emaitzak, '/emaitzak')
    api.add_resource(Estropada, '/estropada/<estropada_id>')
    api.add_resource(Taldeak, '/taldeak')
    api.add_resource(TaldeakByLeague, '/taldeak/<league>')
    api.add_resource(Plantilla, '/taldeak/<team>/plantilla')


routes(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response


if __name__ == '__main__':
    app.run()
