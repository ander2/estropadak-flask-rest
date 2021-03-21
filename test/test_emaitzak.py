import pytest
import json

from app import app
from app.db_connection import db


@pytest.fixture()
def estropadakApp():
    return app.test_client()


@pytest.fixture()
def clean_up():
    yield
    docs = [
        '2019-06-18_ARC1_San-Juan',
        '2019-06-18_ARC1_Donostiarra',
    ]
    for doc_id in docs:
        try:
            doc = db[doc_id]
            if doc.exists():
                # with Document(db, doc_id) as doc:
                doc.fetch()
                doc.delete()
        except KeyError:
            pass


def testEmaitzakByCriteria(estropadakApp):
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and": [{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = estropadakApp.get(f'/emaitzak?criteria={json.dumps(query)}')
    emaitzak = json.loads(rv.data.decode('utf-8'))
    assert len(emaitzak['docs']) == 20
    assert emaitzak['total'] == 20


def testEmaitzakByBadCriteria(estropadakApp):
    rv = estropadakApp.get(f'/emaitzak?criteria={"foo"}')
    assert rv.status_code == 400


def testEmaitzakByCriteriaPagination(estropadakApp):
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and": [{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = estropadakApp.get(f'/emaitzak?criteria={json.dumps(query)}&page=0&count=5')
    emaitzak = json.loads(rv.data.decode('utf-8'))
    assert emaitzak['total'] == 20
    assert len(emaitzak['docs']) == 5


@pytest.mark.skip('Test in wrong branch')
def testEmaitzakByCriteriaBadPagination(estropadakApp):
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and": [{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = estropadakApp.get(f'/emaitzak?criteria={json.dumps(query)}&page=2&count=20')
    assert rv.status_code == 400


def testEmaitzakCreationWithoutCredentials(estropadakApp):
    emaitza_data = {
        "talde_izena": "SAN JUAN",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18 12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "talde_izen_normalizatua": "San Juan"
    }
    rv = estropadakApp.post('/emaitzak', json=emaitza_data)
    assert rv.status_code == 401


def testEmaitzakCreationWithCredentials(estropadakApp, credentials, clean_up):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    emaitza_data = {
        "talde_izena": "SAN JUAN",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18 12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza",
        "talde_izen_normalizatua": "San Juan"
    }
    rv = estropadakApp.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201

    rv = estropadakApp.get('/emaitzak/2019-06-18_ARC1_San-Juan')
    assert rv.status_code == 200


def testEmaitzakCreationWithInvalidData(estropadakApp, credentials, clean_up):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    emaitza_data = {
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18 12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza"
    }
    rv = estropadakApp.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 400


def testEmaitzakModificationWithoutCredentials(estropadakApp, credentials, clean_up):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    emaitza_data = {
        "talde_izena": "Donostiarra",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEMU BANDERA",
        "estropada_data": "2019-06-18 12:00",   # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza"
    }
    rv = estropadakApp.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201

    emaitza_data['posizioa'] = 7
    rv = estropadakApp.put(
        '/emaitzak/2019-06-18_ARC1_Donostiarra',
        json=emaitza_data)
    assert rv.status_code == 401


def testEmaitzakModificationWithCredentials(estropadakApp, credentials, clean_up):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    emaitza_data = {
        "talde_izena": "Donostiarra",
        "tanda_postua": 2,
        "tanda": 2,
        "denbora": "20:30,28",
        "posizioa": 6,
        "ziabogak": [
            "2:16",
            "7:36",
            "12:35"
        ],
        "puntuazioa": 7,
        "kalea": 5,
        "estropada_izena": "III. FEGEM BANDERA",
        "estropada_data": "2019-06-18 12:00",  # Fake date, just to not conflict
        "liga": "ARC1",
        "estropada_id": "37a4adac975ce9ab29decb228900718b",
        "type": "emaitza"
    }
    rv = estropadakApp.post(
        '/emaitzak',
        json=emaitza_data,
        headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201

    emaitza_data['posizioa'] = 7
    emaitza_data['kalea'] = 3

    rv = estropadakApp.put(
        '/emaitzak/2019-06-18_ARC1_Donostiarra',
        json=emaitza_data,
        headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 200

    rv = estropadakApp.get(
        '/emaitzak/2019-06-18_ARC1_Donostiarra',
        json=emaitza_data)
    assert rv.status_code == 200
    assert rv.get_json()['posizioa'] == 7
    assert rv.get_json()['kalea'] == 3
