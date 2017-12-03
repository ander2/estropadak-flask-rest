from flask import Flask
from flask_cors import CORS
from estropadak.views import routes

app = Flask(__name__)
routes(app)
cors = CORS(app, resources={r"/estropada[k]?/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(debug=True)
