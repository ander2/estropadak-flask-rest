import datetime
import textdistance

from estropadakparser.estropada.estropada import Estropada
from ...dao.taldeak_dao import TaldeakDAO


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
        'Tolosaldea': 'blue',
        'Urdaibai': 'blue',
        'Zarautz': 'blue',
        'Zumaia': 'red',
        'Zierbena': 'chocolate'
    }
    try:
        return colors[team]
    except KeyError:
        try:
            s = 0
            color = 'blue'
            for k, v in colors.items():
                simmilarity = textdistance.hamming.similarity(k, team.capitalize())
                if simmilarity > s:
                    s = simmilarity
                    color = v
            return color
        except KeyError:
            return 'blue'


def create_id(estropada, emaitza, taldeak):
    data = datetime.datetime.strptime(estropada['data'], '%Y-%m-%d %H:%M')
    if emaitza is not None:
        taldea = TaldeakDAO.get_talde_izena(emaitza["talde_izena"])
        id = f'{data.strftime("%Y-%m-%d")}_{estropada["liga"]}_{taldea}'
    else:
        izena = estropada['izena'].replace(' ', '-')
        id = f'{data.strftime("%Y-%m-%d")}_{estropada["liga"]}_{izena}'
    return id
