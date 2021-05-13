import os

config = {
    'COUCHDB': 'http://couchdb:5984',
    'DBNAME': 'estropadak',
    'DBUSER': 'admin',
    'DBPASS': ''
}

if 'COUCHDB' in os.environ:
    config['COUCHDB'] = os.environ['COUCHDB']

if 'DBNAME' in os.environ:
    config['DBNAME'] = os.environ['DBNAME']

if 'DBUSER' in os.environ:
    config['DBUSER'] = os.environ['DBUSER']

if 'DBPASS' in os.environ:
    config['DBPASS'] = os.environ['DBPASS']

JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
MIN_YEAR = 2002
LEAGUES = ['ACT', 'ARC1', 'ARC2', 'euskotren', 'ETE', 'GBL', 'BBL', 'TXAPELKETAK', 'GTL', 'BTL']
PAGE_SIZE = 50
