import couchdb
import logging
from app.db_connection import db
from flask_restful import Resource, reqparse


class TaldeakDAO:

    @staticmethod
    def get_taldea_by_id(id):
        try:
            taldea = db[id]
        except TypeError as error:
            logging.error("Not found", error)
            taldea = None
        except couchdb.http.ResourceNotFound as error:
            logging.error("Not found", error)
            taldea = None
        return taldea

    @staticmethod
    def get_taldeak(league, year):
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()

        taldeak = []
        try:
            resume = db[f'rank_{league}_{year}']
            all_teams = db['talde_izenak']
            for taldea in resume['stats'].keys():
                alt_names = [alt for alt, name in all_teams.items() if name == taldea]
                taldeak.append({'name': taldea, 'alt_names': alt_names})
        except couchdb.http.ResourceNotFound as error:
            logging.error("Not found", error)
        return taldeak


class Taldeak(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('league', type=str)
        parser.add_argument('year', type=int)
        args = parser.parse_args()
        teams = []
        league = args.get('league')
        year = args.get('year')
        teams = TaldeakDAO.get_taldeak(league, year)
        return teams
            

class TaldeakByLeague(Resource):
    def get(self, league):
        parser = reqparse.RequestParser()
        parser.add_argument('year', type=int)
        args = parser.parse_args()
        teams = TaldeakDAO.get_taldeak(league, args.get('year', 2019))
        return teams
            
class Plantilla(Resource):
    def get(self, team):
        parser = reqparse.RequestParser()
        parser.add_argument('year', type=int, required=True)
        parser.add_argument('league', type=str, required=True)
        args = parser.parse_args()
        teams = TaldeakDAO.get_taldeak(args['league'], args['year'], team)
        return teams

class TaldeakByName(Resource):
    def get(self, talde_izena, league_id=None):
        all_names = db['talde_izenak']
        normalized_name = all_names[talde_izena]
        names = [key for key, val in all_names.items() if val == normalized_name]
        result = []
        for name in names:
            estropadak = EstropadakDAO.get_estropadak_by_team(name, league_id)
            result.extend(estropadak)
        return [res.format_for_json(res) for res in result]
            