import os
import datetime
import json
import logging
import pytest
from app import app


@pytest.fixture()
def estropadakApp():
    return app.app.test_client()

def testTaldeak(estropadakApp):
    rv = estropadakApp.get('/taldeak?league=ACT&year=2019')
    taldeak = json.loads(rv.data.decode('utf-8'))
    assert len(taldeak) == 12
    assert all(['name' in taldea for taldea in taldeak]) 
    assert all(['alt_names' in taldea for taldea in taldeak]) 