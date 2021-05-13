import json
import logging
import pytest
from app.config import LEAGUES
from app import app


@pytest.fixture()
def estropadakApp():
    return app.test_client()


def testYears(estropadakApp):
    rv = estropadakApp.get('/years')
    logging.info(rv)
    years = json.loads(rv.data.decode('utf-8'))
    supported_leagues = ['act', 'arc1', 'arc2', 'euskotren', 'ete', 'gbl', 'bbl', 'gtl', 'btl', 'txapelketak']
    for res in years:
        assert res['name'] in supported_leagues
        if res['name'] == 'act':
            assert min(res['years']) > 2002
        elif res['name'] == 'arc1' or res['name'] == 'arc2':
            assert min(res['years']) > 2005
        elif res['name'] == 'euskotren':
            assert min(res['years']) > 2008
        elif res['name'] == 'ete':
            assert min(res['years']) > 2017


def testYearsByLeague(estropadakApp):
    rv = estropadakApp.get('/years/act')
    res = json.loads(rv.data.decode('utf-8'))
    assert len(res['years']) > 0


def testYearsPutProtectedEndpointWithoutCredentials(estropadakApp):
    rv = estropadakApp.put('/years/act', json={'urteak': list(range(2003, 2022))})
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
