from app.db_connection import get_db_connection


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
        with get_db_connection() as database:
            try:
                ranks = database.get_view_result("estropadak", "rank",
                                                 raw_result=True,
                                                 startkey=start,
                                                 endkey=end,
                                                 include_docs=True,
                                                 reduce=False)
                result = []
                for rank in ranks['rows']:
                    result.append(rank['doc'])
                return result
            except KeyError:
                return {'error': 'Estropadak not found'}, 404
            return result

    @staticmethod
    def get_sailkapena_by_id(id: str):
        with get_db_connection() as database:
            try:
                return database[id]
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

            