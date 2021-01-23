import time
from cloudant.client import CouchDB
from app.config import config

db = None
while db is None:
    try:
        couch_client = CouchDB(config['DBUSER'], config['DBPASS'],
            url=config['COUCHDB'], connect=True,
            auto_renew=True)
        db = couch_client[config['DBNAME']]
    except:
        print('Cannot connect to DB. Retrying...')
        time.sleep(2)
        pass
