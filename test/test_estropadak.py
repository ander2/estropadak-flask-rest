import os
import datetime
import json
import logging
import pytest
from app import app

class TestEstropadak():

    @pytest.fixture()
    def estropadakApp(self):
        return app.app.test_client()

    def tearDown(self):
        pass
        #os.close(self.db_fd)
        #os.unlink(index.app.config['DATABASE'])

    def testYears(self, estropadakApp):
        rv = estropadakApp.get('/years')
        years = json.loads(rv.data.decode('utf-8'))
        supported_leagues = ['act', 'arc1', 'arc2', 'euskotren', 'ete', 'gbl']
        assert all(year in supported_leagues for year in years.keys())

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
        estropadak = json.loads(rv.data.decode('utf-8'))
        assert len(estropadak) == 0

    def testEstropadakListWithWrongLeague(self, estropadakApp):
        rv = estropadakApp.get('/estropadak?league=actt&year=2010')
        estropadak = json.loads(rv.data.decode('utf-8'))
        assert len(estropadak) == 0

    def testEstropada(self, estropadakApp):
        rv = estropadakApp.get('/estropada/1c79d46b8c74ad399d54fd7ee40005e3')
        estropada = json.loads(rv.data.decode('utf-8'))
        assert estropada['izena'] == 'III Bandera Euskadi Basque Country'

    def testEstropadaNotFound(self, estropadakApp):
        rv = estropadakApp.get('/estropada/fuck')
        estropada = json.loads(rv.data.decode('utf-8'))
        assert estropada == {}


    def testEmaitzak(self, estropadakApp):
        rv = estropadakApp.get('/emaitzak?league=act&year=2010')
        emaitzak = json.loads(rv.data.decode('utf-8'))
        assert len(emaitzak) == 20
