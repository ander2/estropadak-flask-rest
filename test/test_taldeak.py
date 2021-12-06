import json
import pytest
from app import app


@pytest.fixture()
def estropadakApp():
    return app.test_client()


def testTaldeak(estropadakApp):
    rv = estropadakApp.get('/taldeak?league=ACT&year=2019')
    taldeak = json.loads(rv.data.decode('utf-8'))
    assert len(taldeak) == 12
    assert all(['name' in taldea for taldea in taldeak])
    assert all(['alt_names' in taldea for taldea in taldeak])
    assert all(['short' in taldea for taldea in taldeak])


@pytest.mark.parametrize('year, league',
                         [('aaa', 'ACT'),
                          ('', 'AT'),
                          (2015, 1),
                          (2015, 'ATC')])
def testTaldeakInvalidParams(estropadakApp, year, league):
    rv = estropadakApp.get(f'/taldeak?league={league}&year={year}')
    assert rv.status_code == 400
