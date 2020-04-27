import datetime
import json
import pytest
from app import app


class TestEstropadak():

    @pytest.fixture()
    def estropadakApp(self):
        return app.app.test_client()

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

    def testEstropadakListWithoutResults(self, estropadakApp):
        rv = estropadakApp.get('/estropadak?league=act&year=1900')
        assert rv.status_code == 400

    def testEstropadakListWithWrongLeague(self, estropadakApp):
        rv = estropadakApp.get('/estropadak?league=actt&year=2010')
        assert rv.status_code == 400

    def testEstropada(self, estropadakApp):
        rv = estropadakApp.get('/estropadak/1c79d46b8c74ad399d54fd7ee40005e3')
        estropada = json.loads(rv.data.decode('utf-8'))
        assert estropada['izena'] == 'III Bandera Euskadi Basque Country'

    def testEstropadaNotFound(self, estropadakApp):
        rv = estropadakApp.get('/estropadak/fuck')
        # estropada = json.loads(rv.data.decode('utf-8'))
        assert rv.status_code == 404
