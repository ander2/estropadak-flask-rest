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


class TestEstropadak():

    @pytest.fixture()
    def estropadakApp(self):
        return app.test_client()

    def tearDown(self):
        pass

    def testActiveYear(self, estropadakApp):
        rv = estropadakApp.get('/active_year')
        year = json.loads(rv.data.decode('utf-8'))
        n = datetime.datetime.now()
        y = n.year
        assert year == y or year == y-1

    def testEstropadakList(self, estropadakApp):
        rv = estropadakApp.get('/estropadak?league=act&year=2010', )
        estropadak = json.loads(rv.data.decode('utf-8'))
        assert len(estropadak) == 20
        assert estropadak[0]['id'] == "2010-07-03_ACT_I-Bandera-SEAT---G.P.-Villa-de-Bilbao"
        assert estropadak[0]["izena"] == "I Bandera SEAT - G.P. Villa de Bilbao"
        assert estropadak[0]["data"] == "2010-07-03T17:00:00"
        assert estropadak[0]["liga"] == "ACT"
        assert estropadak[0]["urla"] == "http://www.euskolabelliga.com/resultados/ver.php?id=eu&r=1269258408"
        assert estropadak[0]["lekua"] == "Bilbao Bizkaia"
        assert estropadak[0]["kategoriak"] == []

    def testEstropadakListWithoutResults(self, estropadakApp):
        rv = estropadakApp.get('/estropadak?league=act&year=1900')
        assert rv.status_code == 400

    def testEstropadakListWithWrongLeague(self, estropadakApp):
        rv = estropadakApp.get('/estropadak?league=actt&year=2010')
        assert rv.status_code == 400

    def testEstropadakWithoutParams(self, estropadakApp):
        rv = estropadakApp.get('/estropadak')
        assert rv.status_code == 200

    def testEstropadakWithBadPaginationParams(self, estropadakApp):
        rv = estropadakApp.get('/estropadak?page=r')
        assert rv.status_code == 400
        rv = estropadakApp.get('/estropadak?count=r')
        assert rv.status_code == 400

    def testEstropadakWithDefaultPaginationParams(self, estropadakApp):
        rv = estropadakApp.get('/estropadak')
        assert rv.status_code == 200
        print(rv.get_json())
        assert len(rv.get_json()) == 50

    def testEstropada(self, estropadakApp):
        rv = estropadakApp.get('/estropadak/1c79d46b8c74ad399d54fd7ee40005e3')
        estropada = json.loads(rv.data.decode('utf-8'))
        assert estropada['izena'] == 'III Bandera Euskadi Basque Country'

    def testEstropadaNotFound(self, estropadakApp):
        rv = estropadakApp.get('/estropadak/fuck')
        # estropada = json.loads(rv.data.decode('utf-8'))
        assert rv.status_code == 404

    def testEstropadaCreationWithCredentials(self, estropadakApp, credentials):
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

    def testEstropadaCreationWithoutCredentials(self, estropadakApp, credentials, clean_up):
        rv = estropadakApp.post('/estropadak', json={
            "izena": "Estropada test",
            "data": "2021-06-01 17:00",
            "liga": "ACT",
            "sailkapena": []
        })
        assert rv.status_code == 401

    def testEstropadaModificationWithoutCredentials(self, estropadakApp, credentials):
        rv = estropadakApp.put('/estropadak/2021_act_estropada', json={
            "izena": "Estropada test",
            "data": "2021-06-01 17:00",
            "liga": "ACT",
            "sailkapena": [],
        })
        assert rv.status_code == 401

    def testEstropadaModificationWithCredentials(self, estropadakApp, credentials, clean_up):
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

    def testEstropadaDeletionWithoutCredentials(self, estropadakApp, credentials, clean_up):
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

    def testEstropadaDeletionWithCredentials(self, estropadakApp, credentials):
        rv = estropadakApp.post('/auth', json=credentials)
        token = rv.json['access_token']
        rv = estropadakApp.post('/estropadak', json={
            "izena": "Estropada test3",
            "data": "2021-06-02 17:00",
            "liga": "ARC1",
            "sailkapena": []
        }, headers=[('Authorization', f'JWT {token}')])
        assert rv.status_code == 201
        rv = estropadakApp.delete('/estropadak/2021-06-02_ARC1_Estropada-test3', headers=[('Authorization', f'JWT {token}')])
        assert rv.status_code == 200

    def testEstropadaCreationWithMissingDataInModel(self, estropadakApp, credentials):
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

    def testEstropadaCreationWithUnsupportedLiga(self, estropadakApp, credentials):
        rv = estropadakApp.post('/auth', json=credentials)
        token = rv.json['access_token']
        rv = estropadakApp.post('/estropadak', json={
            "izena": "Estropada test5",
            "liga": "ACTT",
            "data": "2021-06-10 17:00",
            "sailkapena": []
        }, headers=[('Authorization', f'JWT {token}')])
        assert rv.status_code == 400

    def testEstropadaCreationWithSailkapena(self, estropadakApp, credentials):
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

    def test_estropada_with_two_day_sailkapena(self, estropadakApp):
        rv = estropadakApp.get('/estropadak/2021-07-03_ACT_V-Bandeira-cidade-da-Coruña-(J1)')
        estropada = json.loads(rv.data.decode('utf-8'))
        assert len(estropada['bi_eguneko_sailkapena']) == 12
        for sailk in estropada['bi_eguneko_sailkapena']:
            if sailk['talde_izena'] == 'GO FIT HONDARRIBIA':
                assert sailk['denbora_batura'] == '41:22,44'
