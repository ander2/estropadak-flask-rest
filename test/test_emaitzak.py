import pytest
import json

from app import app


@pytest.fixture()
def estropadakApp():
    return app.test_client()


def testEmaitzakByCriteria(estropadakApp):
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and":[{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = estropadakApp.get(f'/emaitzak?criteria={json.dumps(query)}')
    emaitzak = json.loads(rv.data.decode('utf-8'))
    assert len(emaitzak) == 20


def testEmaitzakByBadCriteria(estropadakApp):
    rv = estropadakApp.get(f'/emaitzak?criteria={"foo"}')
    assert rv.status_code == 400

def testEmaitzakByCriteriaPagination(estropadakApp):
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and":[{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = estropadakApp.get(f'/emaitzak?criteria={json.dumps(query)}&page=0&count=5')
    emaitzak = json.loads(rv.data.decode('utf-8'))
    assert len(emaitzak) == 5

def testEmaitzakByCriteriaBadPagination(estropadakApp):
    query = {
        "type": "emaitza",
        "liga": "ACT",
        "estropada_data": {
            "$and":[{
                "$gt": "2019-01-01"
            }, {
                "$lt": "2019-12-31"
            }
            ]
        },
        "talde_izen_normalizatua": "Hondarribia"
    }
    rv = estropadakApp.get(f'/emaitzak?criteria={json.dumps(query)}&page=2&count=20')
    assert rv.status_code == 400
