import json
import logging
import pytest
from app import app


@pytest.fixture()
def estropadakApp():
    return app.app.test_client()


def testYears(estropadakApp):
    rv = estropadakApp.get('/years')
    logging.info(rv)
    years = json.loads(rv.data.decode('utf-8'))
    supported_leagues = ['act', 'arc1', 'arc2', 'euskotren', 'ete', 'gbl', 'txapelketak']
    assert all(year in supported_leagues for year in years.keys())
