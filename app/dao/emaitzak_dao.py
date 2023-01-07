import datetime

from app.db_connection import get_db_connection
from ..resources.common.utils import estropadak_transform
from ..resources.taldeak import TaldeakDAO


class EmaitzakDAO:

    @staticmethod
    def get_emaitza_by_id(id):
        with get_db_connection() as database:
            try:
                emaitza = database[id]
            except KeyError:
                emaitza = None
            return emaitza

    @staticmethod
    def get_emaitzak_by_league_year(league, year, team=None):
        league = league.upper()
        if league.lower() == 'euskotren':
            league = league.lower()
        if year:
            start = [league, team, year]
            end = [league, team, year + 1]
        else:
            start = [league, team]
            end = [league, team + 'z']

        with get_db_connection() as database:
            emaitzak = database.get_view_result("emaitzak", "by_team",
                                                startkey=start,
                                                endkey=end,
                                                include_docs=False,
                                                reduce=False)
            result = []
            for emaitza in emaitzak:
                result.append(database[emaitza['id']])
            return result

    @staticmethod
    def get_estropadak_by_team(team, league_id):
        start = [team]
        if league_id:
            start.append(league_id)
        end = ["{}z".format(team)]
        if league_id:
            end.append(league_id)
        with get_db_connection() as database:
            try:
                estropadak = database.view("estropadak/by_team",
                                           estropadak_transform,
                                           startkey=start,
                                           endkey=end,
                                           include_docs=True,
                                           reduce=False)
                result = []
                for estropada in estropadak.rows:
                    result.append(estropada)
                return result
            except KeyError:
                return {'error': 'Estropadak not found'}, 404

    @staticmethod
    def get_emaitzak(criteria: dict, page: int, count: int):
        start = page * count
        end = start + count
        docs = []
        total = 0
        if 'liga' in criteria:
            if criteria['liga'] == 'EUSKOTREN':
                criteria['liga'] = criteria['liga'].lower()
        with get_db_connection() as database:
            emaitzak = database.get_query_result(criteria)
            try:
                for emaitza in emaitzak:
                    total = total + 1
                emaitzak = database.get_query_result(criteria)
                docs = emaitzak[start:end]
            except IndexError:
                return {'error': 'Bad pagination'}, 400
            return (docs, total,)

    @staticmethod
    def insert_emaitza_into_db(emaitza):
        data = datetime.datetime.fromisoformat(emaitza['estropada_data'])
        talde_izen_normalizatua = TaldeakDAO.get_talde_izen_normalizatua(emaitza['talde_izena'])
        izena = talde_izen_normalizatua.replace(' ', '-')
        emaitza['_id'] = f'{data.strftime("%Y-%m-%d")}_{emaitza["liga"]}_{izena}'

        with get_db_connection() as database:
            document = database.create_document(emaitza)
            return document.exists()

    @staticmethod
    def update_emaitza_into_db(emaitza_id, emaitza):
        with get_db_connection() as database:
            document = database[emaitza_id]
            if document.exists():
                document.update(emaitza)
                document.save()
                return document.exists()
            else:
                return None

    @staticmethod
    def delete_emaitza_from_db(emaitza_id):
        with get_db_connection() as database:
            document = database[emaitza_id]
            if document.exists():
                document.fetch()
                document.delete()
                return True
        return False
