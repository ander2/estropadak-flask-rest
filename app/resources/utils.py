import logging
import app.config

from estropadakparser.estropada.estropada import Estropada, TaldeEmaitza
from flask_restx import reqparse


def normalize_id(row):
    if 'doc' in row:
        row['doc']['id'] = row['doc']['_id']
        del row['doc']['_id']
        del row['doc']['_rev']
    else:
        row['id'] = row['_id']
        del row['_id']
        del row['_rev']
    return row


def estropadak_transform(row):
    if 'doc' in row:
        document = row['doc']
    else:
        document = row
    row = normalize_id(row)
    izena = document['izena']
    if 'sailkapena' not in document:
        document['sailkapena'] = []
    sailkapena = document['sailkapena']
    del(document['izena'])
    del(document['sailkapena'])
    estropada = Estropada(izena, **document)
    logging.info(estropada)
    for sailk in sailkapena:
        estropada.taldeak_add(TaldeEmaitza(**sailk))
    return estropada


league_year_parser = reqparse.RequestParser()
league_year_parser.add_argument('league', type=str, choices=app.config.LEAGUES, case_sensitive=False)
league_year_parser.add_argument('year', type=int)

required_league_year_parser = reqparse.RequestParser()
required_league_year_parser.add_argument('league',
                                         type=str, choices=app.config.LEAGUES,
                                         case_sensitive=False, required=True)
required_league_year_parser.add_argument('year', type=int, required=True)


def get_team_color(team: str):
    colors = {
        'Arkote': 'yellow',
        'Astillero': 'navy',
        'Cabo': 'red',
        'Castro': 'red',
        'Deustu': 'red',
        'Donostiarra': 'LightBlue',
        'Getaria': 'wheat',
        'Hondarribia': 'LimeGreen',
        'Hibaika': 'black',
        'Isuntza': 'LightBlue',
        'Orio': 'yellow',
        'Itsasoko ama': 'purple',
        'Kaiku': 'green',
        'Ondarroa': 'red',
        'Portugalete': 'yellow',
        'San Juan': 'pink',
        'San Pedro': 'purple',
        'Tiran': 'blue',
        'Urdaibai': 'blue',
        'Zarautz': 'blue',
        'Zumaia': 'red',
        'Zierbena': 'chocolate'
    }
    try:
        return colors[team]
    except KeyError:
        return 'blue'
