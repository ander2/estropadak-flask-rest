import logging
from app.db_connection import get_db_connection


class EstatistikakDAO:
    @staticmethod
    def get_sailkapena_by_league_year(league, year, category):
        if league in ['gbl', 'bbl', 'btl', 'gtl']:
            _category = category.replace(' ', '_').lower()
            key = 'rank_{}_{}_{}'.format(league.upper(), year, _category)
        else:
            key = 'rank_{}_{}'.format(league.upper(), year)
        with get_db_connection() as database:
            try:
                logging.info(f'Getting {key}')
                doc = database[key]
            except KeyError:
                return None
            result = doc
            return result

    @staticmethod
    def get_sailkapenak_by_league(league):
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
