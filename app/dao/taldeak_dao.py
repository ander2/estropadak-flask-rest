import textdistance
import logging

from app.db_connection import get_db_connection


class TaldeakDAO:

    @staticmethod
    def get_taldea_by_id(id):
        with get_db_connection() as database:
            try:
                taldea = database[id]
            except TypeError:
                logging.info("Not found", exc_info=1)
                taldea = None
            except KeyError:
                logging.info("Not found", exc_info=1)
                taldea = None
            return taldea

    @staticmethod
    def get_taldeak(league, year=None, category=None):
        league = league.upper()

        taldeak = []
        with get_db_connection() as database:
            try:
                all_teams = database['talde_izenak2']
                if year is not None:
                    key = f'rank_{league}_{year}'
                    if category:
                        key = f'rank_{league}_{year}_{category.lower()}'
                    resume = database[key]
                    for taldea in resume['stats'].keys():
                        try:
                            short = all_teams[taldea.title()].get('acronym')
                        except KeyError:
                            s = 0
                            for k in all_teams.keys():
                                simmilarity = textdistance.hamming.similarity(k, taldea.capitalize())
                                if simmilarity > s:
                                    s = simmilarity
                                    team = k
                            short = all_teams[team].get('acronym') + taldea[-2]
                        taldeak.append({
                            "name": taldea,
                            "alt_names": all_teams.get(taldea, {}).get('alt_names', [taldea]),
                            "short": short
                        })
                else:
                    league = league.lower()
                    resume = database[f'taldeak_{league}']
                    for taldea in resume['taldeak']:
                        taldeak.append({
                            "name": taldea,
                            "alt_names": all_teams[taldea].get('alt_names'),
                            "short": all_teams[taldea].get('acronym')
                        })
            except KeyError:
                logging.info("Not found", exc_info=1)
            return taldeak

    @staticmethod
    def get_talde_izen_normalizatua(taldea):
        with get_db_connection() as database:
            talde_izenak = database['talde_izenak']
            try:
                talde_izena = talde_izenak[taldea]
            except KeyError:
                talde_izena = talde_izenak[taldea.title()]
            return talde_izena

    @staticmethod
    def get_talde_izena(taldea):
        talde_izena = ''
        talde_izenak = {} 
        with get_db_connection() as database:
            talde_izenak2 = database['talde_izenak2']
            for k, v in talde_izenak2.items():
                if k.startswith('_'):
                    continue
                for alt_name in v['alt_names']:
                    talde_izenak[alt_name] = k

            try:
                talde_izena = talde_izenak[taldea]
            except KeyError as e:
                print(e)
                talde_izena = talde_izenak[taldea.title()]
        return talde_izena
