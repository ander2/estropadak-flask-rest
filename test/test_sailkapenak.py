import pytest
import json
from app import app


@pytest.fixture()
def estropadakApp():
    return app.test_client()


def testSailkapenaWithLoweCaseLeague(estropadakApp):
    rv = estropadakApp.get('/sailkapenak?league=act&year=2017')
    sailkapena = json.loads(rv.data.decode('utf-8'))
    assert len(sailkapena[0]['stats'].keys()) == 12


def testSailkapenaWithUpperCaseLeague(estropadakApp):
    rv = estropadakApp.get('/sailkapenak?league=act&year=2017')
    sailkapena = json.loads(rv.data.decode('utf-8'))
    assert len(sailkapena[0]['stats'].keys()) == 12


def testSailkapenaForTeam(estropadakApp):
    rv = estropadakApp.get('/sailkapenak?league=act&year=2017&team=Orio')
    sailkapena = json.loads(rv.data.decode('utf-8'))
    keys = ['wins', 'positions', 'position', 'points', 'best', 'worst', 'cumulative', 'age', 'rowers']
    print(sailkapena)
    assert all(izenburua in keys for izenburua in sailkapena[0]['stats']['Orio'].keys())


def testSailkapenaForTeamThatNotExists(estropadakApp):
    rv = estropadakApp.get('/sailkapenak?league=act&team=Oria')
    assert rv.status_code == 200
    assert json.loads(rv.data) == []


def testSailkapenaForTeamWithYearThatNotExists(estropadakApp):
    rv = estropadakApp.get('/sailkapenak?league=act&year=1900&team=Orio')
    assert rv.status_code == 400
