import datetime
import json
import pytest
from app import app
from app.db_connection import get_db_connection


@pytest.fixture()
def clean_up():
    print("setup")
    yield
    print("deleting")
    docs = [
        '2021-06-01_ACT_Estropada-test',
        '2021-06-01_ARC1_Estropada-test2',
        '2021-06-02_ARC1_Estropada-test4',
        '2021-06-01_ACT_Kaiku'
    ]
    with get_db_connection() as database:
        for doc_id in docs:
            try:
                doc = database[doc_id]
                if doc.exists():
                    doc.fetch()
                    doc.delete()
            except KeyError:
                pass


@pytest.fixture()
def two_day_competition():
    print("setup")
    docs = [{
        "_id": "2021-06-01_ACT_J1",
        "data": "2021-06-01T18:00:00",
        "izena": "J1",
        "liga": "ACT",
        "urla": "http://foo.com",
        "bi_jardunaldiko_bandera": True,
        "jardunaldia": 1,
        "related_estropada": "2021-06-02_ACT_J2"
    }, {
        "_id": "2021-06-02_ACT_J2",
        "data": "2021-06-02T18:00:00",
        "izena": "J2",
        "liga": "ACT",
        "urla": "http://foo.com",
        "bi_jardunaldiko_bandera": True,
        "jardunaldia": 2,
        "related_estropada": "2021-06-01_ACT_J1"
    }]
    with get_db_connection() as database:
        for doc in docs:
            try:
                docum = database.create_document(doc)
                print(f"Created {docum['_id']}")
            except KeyError:
                pass
        yield
        for doc in docs:
            try:
                doc = database[doc['_id']]
                print(f"Deleted {doc['_id']}")
                if doc.exists():
                    doc.fetch()
                    doc.delete()
            except KeyError:
                pass


@pytest.fixture()
def estropadakApp():
    return app.test_client()


def tearDown(self):
    pass


def testActiveYear(estropadakApp):
    rv = estropadakApp.get('/active_year')
    year = json.loads(rv.data.decode('utf-8'))
    n = datetime.datetime.now()
    y = n.year
    assert year == y or year == y-1


def test_estropadak_list(estropadakApp):
    rv = estropadakApp.get('/estropadak?league=act&year=2010', )
    estropadak = json.loads(rv.data.decode('utf-8'))
    assert 'docs' in estropadak
    assert 'total' in estropadak
    assert len(estropadak['docs']) == 20
    assert estropadak['total'] == 20
    assert estropadak['docs'][0]['id'] == "2010-07-03_ACT_I-Bandera-SEAT---G.P.-Villa-de-Bilbao"
    assert estropadak['docs'][0]["izena"] == "I Bandera SEAT - G.P. Villa de Bilbao"
    assert estropadak['docs'][0]["data"] == "2010-07-03T17:00:00"
    assert estropadak['docs'][0]["liga"] == "ACT"
    assert estropadak['docs'][0]["urla"] == "http://www.euskolabelliga.com/resultados/ver.php?id=eu&r=1269258408"
    assert estropadak['docs'][0]["lekua"] == "Bilbao Bizkaia"
    assert estropadak['docs'][0]["kategoriak"] == []


def test_estropadak_list_without_results(estropadakApp):
    rv = estropadakApp.get('/estropadak?league=act&year=1900')
    assert rv.status_code == 200
    estropadak = json.loads(rv.data.decode('utf-8'))
    assert estropadak['total'] == 0


def test_estropadak_list_with_wrong_league(estropadakApp):
    rv = estropadakApp.get('/estropadak?league=actt&year=2010')
    assert rv.status_code == 400


def test_estropadak_list_with_Euskotren_league(estropadakApp):
    rv = estropadakApp.get('/estropadak?league=EUSKOTREN&year=2020')
    assert rv.status_code == 200
    estropadak = json.loads(rv.data.decode('utf-8'))
    assert estropadak['total'] == 14


def test_estropadak_without_params(estropadakApp):
    rv = estropadakApp.get('/estropadak')
    assert rv.status_code == 200


def test_estropadak_with_bad_pagination_params(estropadakApp):
    rv = estropadakApp.get('/estropadak?page=r')
    assert rv.status_code == 400
    rv = estropadakApp.get('/estropadak?count=r')
    assert rv.status_code == 400


def test_estropadak_with_default_pagination_params(estropadakApp):
    rv = estropadakApp.get('/estropadak')
    assert rv.status_code == 200
    estropadak = rv.get_json()
    assert len(estropadak['docs']) == 50


def test_estropada(estropadakApp):
    rv = estropadakApp.get('/estropadak/1c79d46b8c74ad399d54fd7ee40005e3')
    estropada = json.loads(rv.data.decode('utf-8'))
    assert estropada['izena'] == 'III Bandera Euskadi Basque Country'


def test_estropada_not_found(estropadakApp):
    rv = estropadakApp.get('/estropadak/fuck')
    assert rv.status_code == 404


def test_estropada_creation_with_credentials(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "ACT",
        "sailkapena": [],
        "lekua": "Nonbait"
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201


def test_estropada_creation_with_credentials_Euskotren_liga(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "EUSKOTREN",
        "sailkapena": [],
        "lekua": "Nonbait"
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201


def test_estropada_creation_without_credentials(estropadakApp, credentials, clean_up):
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "ACT",
        "sailkapena": []
    })
    assert rv.status_code == 401


def test_estropada_modification_without_credentials(estropadakApp, credentials):
    rv = estropadakApp.put('/estropadak/2021_act_estropada', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "ACT",
        "sailkapena": [],
    })
    assert rv.status_code == 401


def test_estropada_modification_with_credentials(estropadakApp, credentials, clean_up):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test2",
        "data": "2021-06-01 17:00",
        "liga": "ARC1",
        "sailkapena": []
    }, headers=[('Authorization', f'JWT {token}')])
    rv = estropadakApp.put('/estropadak/2021-06-01_ARC1_Estropada-test2', json={
        "izena": "Estropada test2",
        "data": "2021-06-01 17:30",
        "liga": "ARC1",
        "sailkapena": [],
        "lekua": "Nonbait"
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 200
    rv = estropadakApp.get('/estropadak/2021-06-01_ARC1_Estropada-test2')
    recovered_doc = rv.get_json()
    recovered_doc['izena'] == "Estropada test2"
    recovered_doc['data'] == "2021-06-01 17:30"
    recovered_doc['liga'] == "arc1"
    recovered_doc['lekua'] == 'Nonbait'
    recovered_doc['sailkapena'] == []


def test_estropada_deletion_without_credentials(estropadakApp, credentials, clean_up):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test4",
        "data": "2021-06-02 17:00",
        "liga": "ARC1",
        "sailkapena": []
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201
    rv = estropadakApp.delete('/estropadak/2021-06-02_ARC1_Estropada-test4')
    assert rv.status_code == 401


def test_estropada_deletion_with_credentials(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test3",
        "data": "2021-06-02 17:00",
        "liga": "ARC1",
        "sailkapena": []
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201
    rv = estropadakApp.delete('/estropadak/2021-06-02_ARC1_Estropada-test3',
                              headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 200


def test_estropada_creation_with_missing_data_in_model(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test5",
        "data": "2021-06-10 17:00",
        "sailkapena": []
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 400

    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test5",
        "liga": "ARC1",
        "sailkapena": []
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 400

    rv = estropadakApp.post('/estropadak', json={
        "izena": "",
        "data": "2021-06-10 17:00",
        "liga": "ARC1",
        "sailkapena": []
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 400


def test_estropada_creation_with_unsupported_liga(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test5",
        "liga": "ACTT",
        "data": "2021-06-10 17:00",
        "sailkapena": []
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 400


def test_estropada_creation_with_sailkapena(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/estropadak', json={
        "izena": "Estropada test",
        "data": "2021-06-01 17:00",
        "liga": "ACT",
        "sailkapena": [{
            "talde_izena": "KAIKU",
            "denbora": "20:14,84",
            "puntuazioa": 5,
            "posizioa": 8,
            "tanda": 1,
            "tanda_postua": 1,
            "kalea": 1,
            "ziabogak": [
                "05:06",
                "09:56",
                "15:24"
            ]
        }]
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201
    rv = estropadakApp.get('/estropadak/2021-06-01_ACT_Estropada-test')
    assert rv.status_code == 200
    rv = estropadakApp.get('/emaitzak/2021-06-01_ACT_Kaiku')
    assert rv.status_code == 200


def test_estropada_with_two_day_sailkapena(estropadakApp):
    rv = estropadakApp.get('/estropadak/2021-07-03_ACT_V-Bandeira-cidade-da-Coruña-(J1)')
    estropada = json.loads(rv.data.decode('utf-8'))
    assert len(estropada['bi_eguneko_sailkapena']) == 12
    for sailk in estropada['bi_eguneko_sailkapena']:
        if sailk['talde_izena'] == 'GO FIT HONDARRIBIA':
            assert sailk['denbora_batura'] == '41:22,44'


def test_estropada_with_two_day_sailkapena_still_unplayed(estropadakApp, two_day_competition):
    rv = estropadakApp.get('/estropadak/2021-06-01_ACT_J1')
    estropada = json.loads(rv.data.decode('utf-8'))
    assert len(estropada['bi_eguneko_sailkapena']) == 0
    assert estropada['bi_eguneko_sailkapena'] == []
    assert estropada['related_estropada'] == '2021-06-02_ACT_J2'
    assert estropada['jardunaldia'] == 1
