import logging

from app.db_connection import get_db_connection
from ..config import PAGE_SIZE
from typing import Dict, List


class EstropadakDAO:
    @staticmethod
    def get_estropada_by_id(id):
        with get_db_connection() as database:
            try:
                estropada = database[id]
                estropada['data'] = estropada['data'].replace(' ', 'T')
                if estropada['liga'] == 'euskotren':
                    estropada['liga'] = estropada['liga'].upper()
            except TypeError:
                logging.error("Not found", exc_info=1)
                estropada = None
            except KeyError:
                logging.error("Not found", exc_info=1)
                estropada = None
            return estropada

    @staticmethod
    def get_estropadak_by_league_year(league, year, page=0, count=PAGE_SIZE) -> Dict[str, List[Dict]]:
        logging.info("League:%s and year: %s", league, year)
        start = []
        end = []
        if league:
            league = league.upper()
            if league.lower() == 'euskotren':
                league = league.lower()
            start.append(league)
            end.append(league)

        if year:
            yearz = "{}".format(year)
            fyearz = "{}z".format(year)
            start.append(yearz)
            end.append(fyearz)
        else:
            end = ["{}z".format(league)]

        with get_db_connection() as database:
            try:
                res = database.get_view_result("estropadak", "all",
                                               startkey=start,
                                               endkey=end,
                                               raw_result=True,
                                               reduce=True)
                doc_count = res.get('rows', [{'value': 0}])[0]['value']
                if doc_count > 0:
                    estropadak = database.get_view_result("estropadak",
                                                          "all",
                                                          raw_result=True,
                                                          startkey=start,
                                                          endkey=end,
                                                          include_docs=True,
                                                          reduce=False,
                                                          skip=count * page,
                                                          limit=count)
                    result = []
                    for row in estropadak['rows']:
                        estropada = row['doc']
                        estropada['data'] = estropada['data'].replace(' ', 'T')
                        if estropada['liga'] == 'euskotren':
                            estropada['liga'] = estropada['liga'].upper()
                        result.append(estropada)

                return {
                    'total': doc_count,
                    'docs': result
                }
            except KeyError:
                return {'error': 'Estropadak not found'}, 404

    @staticmethod
    def insert_estropada_into_db(estropada):
        if estropada['liga'] == 'EUSKOTREN':
            estropada['liga'] = estropada['liga'].lower()
        with get_db_connection() as database:
            document = database.create_document(estropada)
            return document.exists()

    @staticmethod
    def update_estropada_into_db(estropada_id, estropada):
        with get_db_connection() as database:
            doc = database[estropada_id]
            doc['izena'] = estropada['izena']
            doc['data'] = estropada['data']
            doc['liga'] = estropada['liga']
            if doc['liga'] == 'EUSKOTREN':
                estropada['liga'] = estropada['liga'].lower()
            doc['lekua'] = estropada['lekua']
            doc['sailkapena'] = estropada['sailkapena']
            doc['type'] = estropada['type']
            if estropada.get('bi_jardunaldiko_bandera'):
                doc['bi_jardunaldiko_bandera'] = estropada['bi_jardunaldiko_bandera']
            if estropada.get('related_estropada'):
                doc['related_estropada'] = estropada['related_estropada']
            if estropada.get('jardunaldia'):
                doc['jardunaldia'] = estropada['jardunaldia']
            if len(estropada.get('kategoriak', [])):
                doc['kategoriak'] = estropada['kategoriak']
            if estropada.get('urla'):
                doc['urla'] = estropada['urla']
            doc.save()

    @staticmethod
    def delete_estropada_from_db(estropada_id):
        with get_db_connection() as database:
            doc = database[estropada_id]
            if doc.exists():
                doc.fetch()
                doc.delete()
