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
        assert all(year in ['act', 'arc1', 'arc2', 'euskotren', 'ete'] for year in years.keys())

    def testActiveYear(self, estropadakApp):
        rv = estropadakApp.get('/active_year')
        year = json.loads(rv.data.decode('utf-8'))
        n = datetime.datetime.now()
        y = n.year
        if (n.month < 5):
            y = n.year - 1
        assert year == y

    def testEstropadakList(self, estropadakApp):
        rv = estropadakApp.get('/estropadak/act/2010')
        estropadak = json.loads(rv.data.decode('utf-8'))
        assert len(estropadak) == 20

    def testEstropadakListWithoutResults(self, estropadakApp):
        rv = estropadakApp.get('/estropadak/act/1900')
        estropadak = json.loads(rv.data.decode('utf-8'))
        assert len(estropadak) == 0

    def testEstropadakListWithWrongLeague(self, estropadakApp):
        rv = estropadakApp.get('/estropadak/actt/2010')
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

    def testSailkapenaWithLoweCaseLeague(self, estropadakApp):
        rv = estropadakApp.get('/sailkapena/act/2017')
        sailkapena = json.loads(rv.data.decode('utf-8'))
        assert len(sailkapena.keys()) == 12

    def testSailkapenaWithUpperCaseLeague(self, estropadakApp):
        rv = estropadakApp.get('/sailkapena/ACT/2017')
        sailkapena = json.loads(rv.data.decode('utf-8'))
        assert len(sailkapena.keys()) == 12

    def testSailkapenaForTeam(self, estropadakApp):
        rv = estropadakApp.get('/sailkapena/ACT/2017/Orio')
        sailkapena = json.loads(rv.data.decode('utf-8'))
        keys = ['wins', 'positions', 'position', 'points', 'best', 'worst', 'cumulative']
        assert all(izenburua in keys for izenburua in sailkapena.keys()) 

    def testSailkapenaForTeamThatNotExists(self, estropadakApp):
        rv = estropadakApp.get('/sailkapena/ACT/2017/Oria')
        assert rv.status_code == 404
        sailkapena = json.loads(rv.data.decode('utf-8'))
        assert sailkapena == {'error': 'Team not found'}

    def testSailkapenaForTeamWithYearThatNotExists(self, estropadakApp):
        rv = estropadakApp.get('/sailkapena/ACT/1900/Orio')
        assert rv.status_code == 404
        sailkapena = json.loads(rv.data.decode('utf-8'))
        assert sailkapena == {'error': 'Stats not found'}
