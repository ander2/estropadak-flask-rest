from app.db_connection import get_db_connection
from typing import List


class SailkapenakDAO:

    @staticmethod
    def get_sailkapena_by_league_year(league, year, category):
        with get_db_connection() as database:
            if league in ['gbl', 'bbl', 'btl', 'gtl']:
                _category = category.replace(' ', '_').lower()
                key = 'rank_{}_{}_{}'.format(league.upper(), year, _category)
            elif league == 'EUSKOTREN':
                key = 'rank_{}_{}'.format(league.lower(), year)
            else:
                key = 'rank_{}_{}'.format(league.upper(), year)
            try:
                doc = database[key]
            except KeyError:
                return None
            result = {
                'total': 1,
                'docs': [doc]
            }
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
        with get_db_connection() as database:
            try:
                result = []
                ranks = database.get_view_result("estropadak", "rank",
                                                 raw_result=True,
                                                 startkey=start,
                                                 endkey=end,
                                                 reduce=True)
                count = ranks.get('rows', [{'value': 0}])[0]['value']
                if count > 0:
                    ranks = database.get_view_result("estropadak", "rank",
                                                     raw_result=True,
                                                     startkey=start,
                                                     endkey=end,
                                                     include_docs=True,
                                                     reduce=False)
                    for rank in ranks['rows']:
                        result.append(rank['doc'])
            except KeyError:
                return {'error': 'Estropadak not found'}, 404
            return {
                'total': count,
                'docs': result
            }

    @staticmethod
    def get_sailkapena_by_id(id: str):
        with get_db_connection() as database:
            try:
                return database[id]
            except KeyError:
                return None  # {'error': 'Sailkapena not found'}, 404

    @staticmethod
    def get_sailkapenak_by_teams(league: str, year: str, teams: List[str]):
        with get_db_connection() as database:
            try:
                doc_count = 0
                result = []
                for team in teams:
                    key = [team, league, year]
                    sailkapenak_count = database.get_view_result("sailkapenak", "by_team",
                                                                 key=key,
                                                                 include_docs=False,
                                                                 raw_result=True,
                                                                 reduce=True)
                    if len(sailkapenak_count['rows']) > 0:
                        doc_count = doc_count + sailkapenak_count.get('rows', [{'value': 0}])[0]['value']
                        sailkapenak = database.get_view_result("sailkapenak", "by_team",
                                                               key=key,
                                                               include_docs=False,
                                                               raw_result=True,
                                                               reduce=False)
                        for emaitza in sailkapenak['rows']:
                            doc = database[emaitza['id']]
                            for name, stat in doc['stats'].items():
                                if name == team:
                                    doc['stats'] = [{
                                        "name": team,
                                        "value": stat
                                    }]
                                    break
                            result.append(doc)
                print(result)
                return {
                    'total': doc_count,
                    'docs': result
                }
            except KeyError:
                return None  # {'error': 'Sailkapena not found'}, 404

    @staticmethod
    def insert_sailkapena_into_db(sailkapena):
        with get_db_connection() as database:
            doc = database.create_document(sailkapena)
            return doc.exists()

    @staticmethod
    def update_sailkapena_into_db(sailkapena_id, sailkapena):
        with get_db_connection() as database:
            doc = database[sailkapena_id]
            doc['stats'] = sailkapena['stats']
            doc.save()

    @staticmethod
    def delete_sailkapena_from_db(sailkapena_id):
        with get_db_connection() as database:
            doc = database[sailkapena_id]
            if doc.exists():
                doc.fetch()
                doc.delete()

            