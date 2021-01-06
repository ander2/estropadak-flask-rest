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

MIN_YEAR = 2002
LEAGUES = ['ACT', 'ARC1', 'ARC2', 'EUSKOTREN', 'ETE', 'GBL', 'TXAPELKETAK']
PAGE_SIZE=50
