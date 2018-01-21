import os

config = {
    'COUCHDB': 'http://couchdb:5984'
}

if 'COUCHDB' in os.environ:
    config['COUCHDB'] = os.environ['COUCHDB']
