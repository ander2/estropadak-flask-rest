import couchdb
from app.config import config

db = None
while db is None:
    try:
        couch_server = couchdb.Server(config['COUCHDB'])
        db = couch_server[config['DBNAME']]
    except:
        pass
