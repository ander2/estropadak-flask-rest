import pytest
import json

from app import app


@pytest.fixture()
def estropadakApp():
    return app.test_client()


def testEmaitzak(estropadakApp):
    rv = estropadakApp.get('/emaitzak?league=act&year=2010')
    emaitzak = json.loads(rv.data.decode('utf-8'))
    assert len(emaitzak) == 20
