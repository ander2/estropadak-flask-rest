import os

config = {
    'COUCHDB': 'http://couchdb:5984',
    'DBNAME': 'estropadak'
}

if 'COUCHDB' in os.environ:
    config['COUCHDB'] = os.environ['COUCHDB']

if 'DBNAME' in os.environ:
    config['DBNAME'] = os.environ['DBNAME']
