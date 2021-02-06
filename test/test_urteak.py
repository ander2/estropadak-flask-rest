import json
import logging
import pytest
from app import app


@pytest.fixture()
def estropadakApp():
    return app.test_client()

@pytest.fixture()
def credentials():
    return dict(username='test_api', password='test_api_pass')

def testYears(estropadakApp):
    rv = estropadakApp.get('/years')
    logging.info(rv)
    years = json.loads(rv.data.decode('utf-8'))
    supported_leagues = ['act', 'arc1', 'arc2', 'euskotren', 'ete', 'gbl', 'txapelketak']
    assert all(year in supported_leagues for year in years.keys())


def testYearsByLeague(estropadakApp):
    rv = estropadakApp.get('/years/act')
    years = json.loads(rv.data.decode('utf-8'))
    assert years[0] == 2003


def testYearsPutProtectedEndpoint(estropadakApp):
    rv = estropadakApp.put('/years/act')
    assert rv.status_code == 401
    

def testYearsPutProtectedEndpoint(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.put('/years/act', json={'urteak': list(range(2003, 2022))}, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 200
    

def testYearsPutBadParams(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    # Bad param name
    rv = estropadakApp.put('/years/act', json={'urte': list(range(2003, 2022))}, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 400

    # Bad values 
    rv = estropadakApp.put('/years/act', json={'urteak': list('abc')}, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 400
