import urllib.parse
import http.client
from app.config import config
import json


users_dict = {}


class Ident:
    def __init__(self, id, data):
        self.id = id
        self.data = data


def authenticate(user, password):
    params = urllib.parse.urlencode({"name": user, "password": password})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    host = config['COUCHDB_HOST']
    port = int(config['COUCHDB_PORT'])
    conn = http.client.HTTPConnection(host, port)
    conn.request("POST", "/_session", params, headers)
    response = conn.getresponse()
    res = json.loads(response.read())

    if 'error' in res:
        return {}
    else:
        res['id'] = res['name']
        user = Ident(res['name'], res)
        users_dict[res['name']] = user
        return user


def identity(payload):
    # @TODO Think about this
    # Naive identity implementation
    return users_dict.get(payload['identity'], None)