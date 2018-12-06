from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from app.resources.estropadak import (ActiveYear,
                                     Emaitzak,
                                     Estropadak, 
                                     Estropada, 
                                     Sailkapena, 
                                     Years, 
                                     Taldeak,
                                     TaldeakByName)

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
    # api.add_resource(TaldeakByName, '/taldeak/<talde_izena>', '/taldeak/<talde_izena>/<league_id>')

routes(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response


if __name__ == '__main__':
    app.run()
