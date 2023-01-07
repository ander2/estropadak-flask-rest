from app.db_connection import get_db_connection


class YearsDAO:
    @staticmethod
    def get_years_from_db():
        with get_db_connection() as database:
            return database['years']

    @staticmethod
    def update_years_into_db(years, league):
        with get_db_connection() as database:
            doc = database['years']
            if league:
                doc[league] = years
            else:
                doc = years
            doc.save()
