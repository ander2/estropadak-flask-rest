import os

config = {
    'COUCHDB': 'http://couchdb:5984',
    'DBNAME': 'estropadak'
}

if 'COUCHDB' in os.environ:
    config['COUCHDB'] = os.environ['COUCHDB']

if 'DBNAME' in os.environ:
    config['DBNAME'] = os.environ['DBNAME']

MIN_YEAR = 2002
LEAGUES = ['ACT', 'ARC1', 'ARC2', 'EUSKOTREN', 'ETE', 'GBL', 'TXAPELKETAK']
PAGE_SIZE=50
