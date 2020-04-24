import logging
from estropadakparser.estropada.estropada import Estropada, TaldeEmaitza


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
    izena = document['izena']
    if 'sailkapena' not in document:
        document['sailkapena'] = []
    sailkapena = document['sailkapena']
    del(document['izena'])
    del(document['sailkapena'])
    estropada = Estropada(izena, **document)
    logging.info(estropada)
    for sailk in sailkapena:
        estropada.taldeak_add(TaldeEmaitza(**sailk))
    return estropada
