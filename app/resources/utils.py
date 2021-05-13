import logging
import app.config
import datetime

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
    izena = document.pop('izena')
    estropada = Estropada(izena, **document)
    return estropada

league_year_parser = reqparse.RequestParser()
league_year_parser.add_argument('league', type=str, choices=app.config.LEAGUES, case_sensitive=False)
league_year_parser.add_argument('year', type=int)
league_year_parser.add_argument('page', type=int, help="Page number", default=0)
league_year_parser.add_argument('count', type=int, help="Elements per page", default=app.config.PAGE_SIZE)

required_league_year_parser = reqparse.RequestParser()
required_league_year_parser.add_argument('league',
                                         type=str, choices=app.config.LEAGUES,
                                         case_sensitive=False, required=True)
required_league_year_parser.add_argument('year', type=int, required=False)


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
        try:
            if team.endswith((' A', ' B', ' C', ' D')):
                team = team[:-2]
            return colors[team.capitalize()]
        except KeyError:
            return 'blue'
 

def create_id(estropada, emaitza, taldeak):
    data = datetime.datetime.strptime(estropada['data'], '%Y-%m-%d %H:%M')
    if emaitza is not None:
        taldea = get_talde_izena(emaitza["talde_izena"])
        id = f'{data.strftime("%Y-%m-%d")}_{estropada["liga"]}_{taldea}'
    else:
        izena = estropada['izena'].replace(' ', '-')
        id = f'{data.strftime("%Y-%m-%d")}_{estropada["liga"]}_{izena}'
    return id
