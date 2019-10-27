import logging
import time
from flask_restful import Resource, reqparse
from estropadakparser.estropada.estropada import Estropada as EstropadaModel, TaldeEmaitza
from app.db_connection import db

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
    estropada = EstropadaModel(izena, **document)
    logging.info(estropada)
    for sailk in sailkapena:
        estropada.taldeak_add(TaldeEmaitza(**sailk))
    return estropada

class SailkapenakDAO:

    @staticmethod
    def get_sailkapena_by_league_year(league, year):
        key = 'rank_{}_{}'.format(league.upper(), year)
        try:
            doc = db[key]
        except couchdb.http.ResourceNotFound:
            return None
        result = [doc]
        return result

    @staticmethod
    def get_sailkapena_by_league(league):
        key = 'rank_{}'.format(league.upper())
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        endkey = "{}z".format(key)

        start = key
        end = endkey
        try:
            ranks = db.view("estropadak/rank",
                                 None,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=True,
                                 reduce=False)
            result = []
            for rank in ranks.rows:
                result.append(rank.doc)
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404
        return result

class EstropadakDAO:
    @staticmethod
    def get_estropadak_by_league_year(league, year):
        logging.info("League:%s and year: %s", league, year)
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        start = [league]
        end = [league]

        if year is not None:
            yearz = "{}".format(year)
            fyearz = "{}z".format(year)
            start.append(yearz)
            end.append(fyearz)
        else:
            end = ["{}z".format(league)]

        try:
            estropadak = db.view("estropadak/all",
                                 None,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=False,
                                 reduce=False)
            result = []
            for estropada in estropadak.rows:
                puntuagarria = True
                if db[estropada.id].get('puntuagarria', True) is False:
                    puntuagarria = False
                result.append({
                    'id': estropada.id,
                    'data':estropada.key[1],
                    'izena': estropada.key[2],
                    'puntuagarria': puntuagarria
                })
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404

class EmaitzakDAO:

    @staticmethod
    def get_estropada_by_id(id):
        try:
            estropada = estropadak_transform(db[id])
        except TypeError as error:
            logging.error("Not found", error)
            estropada = None
        except couchdb.http.ResourceNotFound as error:
            logging.error("Not found", error)
            estropada = None
        return estropada

    @staticmethod
    def get_estropadak_by_league_year(league, year):
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        yearz = "{}".format(year)
        fyearz = "{}z".format(year)

        start = [league, yearz]
        end = [league, fyearz]
        try:
            estropadak = db.view("estropadak/all",
                                 estropadak_transform,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=True,
                                 reduce=False)
            result = []
            for estropada in estropadak.rows:
                result.append(estropada)
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404

    @staticmethod
    def get_estropadak_by_team(team, league_id):
        start = [team]
        if league_id:
            start.append(league_id)
        end = ["{}z".format(team)]
        if league_id:
            end.append(league_id)
        try:
            estropadak = db.view("estropadak/by_team",
                                 estropadak_transform,
                                 startkey=start,
                                 endkey=end,
                                 include_docs=True,
                                 reduce=False)
            result = []
            for estropada in estropadak.rows:
                result.append(estropada)
            return result
        except couchdb.http.ResourceNotFound:
            return {'error': 'Estropadak not found'}, 404


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

class Years(Resource):
    def get(self):
        doc = db['years']
        del doc['_id']
        del doc['_rev']
        return doc

class ActiveYear(Resource):
    def get(self):
        doc = db['active_year']
        return doc['year']


class Estropadak(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('league', type=str)
        parser.add_argument('year', type=str, default=None)
        args = parser.parse_args()
        estropadak = EstropadakDAO.get_estropadak_by_league_year(args['league'], args['year'])
        return estropadak

class Emaitzak(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('league', type=str)
        parser.add_argument('year', type=str)
        args = parser.parse_args()
        estropadak = EmaitzakDAO.get_estropadak_by_league_year(args['league'], args['year'])
        return [estropada.format_for_json(estropada) for estropada in estropadak]

class Estropada(Resource):
    def get(self, estropada_id):
        estropada = EmaitzakDAO.get_estropada_by_id(estropada_id)
        if estropada is None:
            return {}
        else:
            return estropada.format_for_json(estropada)

class Sailkapena(Resource):
    def get(self):
        stats = None
        parser = reqparse.RequestParser()
        parser.add_argument('league', type=str)
        parser.add_argument('year', type=int)
        parser.add_argument('team', type=str)
        args = parser.parse_args()
        if args.get('year', None) is None:
            stats = SailkapenakDAO.get_sailkapena_by_league(args['league'])
        else:
            stats = SailkapenakDAO.get_sailkapena_by_league_year(args['league'], args['year'])
        if stats is None:
            return []

        if args.get('team', None):
            team_stats = []
            for stat in stats:
                try:
                    _stats = stat['stats'][args['team']]
                    team_stats.append({
                        "id": stat.id,
                        "urtea": int(stat.id[-4:]),
                        "stats": {
                            args['team']: _stats
                        } 
                    })
                except KeyError as e:
                    logging.info('Team "%s" not found' % args['team'])
            return team_stats
        else:
            result = [
                {
                    "id": stats[0].id,
                    "urtea": args['year'],
                    "stats": stats[0]['stats']
                }
            ]
            return result
