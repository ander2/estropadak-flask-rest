from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from app.resources.estropadak import ActiveYear, Emaitzak, Estropadak, Estropada, Sailkapena, Years, Taldeak

app = Flask(__name__)

def routes(app):
    api = Api(app)
    api.add_resource(Years, '/years')
    api.add_resource(ActiveYear, '/active_year')
    api.add_resource(Sailkapena, '/sailkapena/<league_id>/<year>', '/sailkapena/<league_id>/<year>/<team>')
    api.add_resource(Estropadak, '/estropadak/<league_id>/<year>')
    api.add_resource(Emaitzak, '/emaitzak/<league_id>/<year>')
    api.add_resource(Estropada, '/estropada/<estropada_id>')
    api.add_resource(Taldeak, '/taldeak/<talde_izena>', '/taldeak/<talde_izena>/<league_id>')

routes(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response


if __name__ == '__main__':
    app.run()
