import time
import contextlib
from cloudant.client import CouchDB
from app.config import config

@contextlib.contextmanager
def get_db_connection():
    client = CouchDB(config['DBUSER'], config['DBPASS'],
        url=config['COUCHDB'], connect=True,
        auto_renew=True)

    db = client[config['DBNAME']]
    try:
        yield db
    finally:
        client.disconnect()
    
    
