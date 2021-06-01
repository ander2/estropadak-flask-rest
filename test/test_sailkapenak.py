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


def test_sailkapena_creation_without_credentials(estropadakApp):
    rv = estropadakApp.post('/sailkapenak', json={
        "league": "ACT",
        "year": 2022,
        "stats": []
    })
    assert rv.status_code == 401


def test_sailkapena_creation_with_credentials(estropadakApp, credentials):
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post('/sailkapenak', json={
        "league": "ACT",
        "year": 2022,
        "stats": [{
            "name": "Donostiarra"
        }]
    }, headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 201


def test_get_sailkapena_for_id(estropadakApp):
    rv = estropadakApp.get('/sailkapenak/rank_ACT_2019')
    assert rv.status_code == 200
    assert rv.json['id'] == 'rank_ACT_2019'
    assert rv.json['year'] == 2019
    assert rv.json['league'] == 'ACT'
    assert len(rv.json['stats']) == 12


def test_put_sailkapena_for_id_without_credentials(estropadakApp):
    rv = estropadakApp.get('/sailkapenak/rank_ACT_2019')
    sailkapena = rv.json
    rv = estropadakApp.put('/sailkapenak/rank_ACT_2019', json=sailkapena)
    assert rv.status_code == 401


def test_put_sailkapena_for_id_with_credentials(estropadakApp, credentials):
    rv = estropadakApp.get('/sailkapenak/rank_ACT_2019')
    sailkapena = rv.json
    sailkapena['stats'].append({
        'name': 'fantomas',
        'value': {
            'best': 1,
            'worst': 2,
            'points': 23,
            'position': 2,
            'positions': [1, 2],
            'cumulative': [12, 23],
        }
    })
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.put(
        '/sailkapenak/rank_ACT_2019',
        json=sailkapena,
        headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 200
    rv = estropadakApp.get('/sailkapenak/rank_ACT_2019')
    sailkapena = rv.json
    assert len(rv.json['stats']) == 13
    fantomas_stats = sailkapena['stats'][12]
    assert fantomas_stats['value']['best'] == 1
    assert fantomas_stats['value']['worst'] == 2
    assert fantomas_stats['value']['points'] == 23
    assert fantomas_stats['value']['position'] == 2
    assert fantomas_stats['value']['positions'] == [1, 2]
    assert fantomas_stats['value']['cumulative'] == [12, 23]
    sailkapena['stats'] = sailkapena['stats'][0:12]
    rv = estropadakApp.put(
        '/sailkapenak/rank_ACT_2019',
        json=sailkapena,
        headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 200


def test_delete_sailkapena_for_id_without_credentials(estropadakApp):
    rv = estropadakApp.delete('/sailkapenak/rank_ACT_2019')
    assert rv.status_code == 401


def test_delete_sailkapena_for_id_with_credentials(estropadakApp, credentials):
    sailkapena = {
        'league': 'ACT',
        'year': 2100,
        'stats': []
    }
    rv = estropadakApp.post('/auth', json=credentials)
    token = rv.json['access_token']
    rv = estropadakApp.post(
        '/sailkapenak',
        json=sailkapena,
        headers=[('Authorization', f'JWT {token}')])
    rv = estropadakApp.delete(
        '/sailkapenak/rank_ACT_2100',
        headers=[('Authorization', f'JWT {token}')])
    assert rv.status_code == 200
