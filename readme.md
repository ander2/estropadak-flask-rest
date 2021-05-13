# Introduction / Sarrera

`flask-restx` implementation of estropadak REST API

Estropadak REST API-aren inplementazioa `flask-restx` erailiz.

# Setup

The API uses a Cochdb database, it should be set with the `COUCHDB` env variable. Use `DBNAME` to specify the database name.
Dependencies can be  installed via PIP, except `estropadak-lxml` wich is not available on PyPi, but you can get [here](https://github.com/ander2/estropadak-lxml)

API-ak Cochdb datubase bat erabiltzen du eta `COUCHDB` ingurune aldagaiaren bidez zehaztu behar da. `DBNAME` datubasearen izena zehazteko erabiltzen da.
Dependentziak PIP bidez instalatu daitezke, `estropadak-lxml` izan ezik, ez baitago PyPi-n eskuragarri, baina [hemen](https://github.com/ander2/estropadak-lxml) lortu dezakezue.


# Usage / Erabilera

Garapen instantzia bat martxan jartzeko:
```
$ COUCHDB=http://localhost:5984 DBNAME=estropadak python3 -m app.app
```

edota `index.py` fitxategi bat sortu erroan hurrengo kodearekin

```
from app.app import app 
app.run(
    debug = True,
	port = 8080
)
```
eta exekutatu:

```
$ python3 index.py
```

# Endpoints

The server exposes a swagger [documentation](http://www.estropadak.eus/doc/api) page on port 5000, but this is a little resume:

These are currently the exposed endpoints:

    * /estropadak : Return list of estropadak for given league and year
    * /estropadak/<estropada_id>: Return estropada for given id
    * /sailkapenak: Return rank for given league and year
    * /emaitzak: Return results for given league and year
    * /emaitzak/<estropada_id>: Return rank for given league and year
    * /taldeak: Return list of team
    * /taldeak/<team>: Return team data
    * /estatistikak: Return estatistics


Zerbitzariak swagger dokumentazio orri bat erakusten du 5000 portuan, baina hau da laburpentxo bat:

Hauek dira eskaintzen diren endpoint-ak:

    * /estropadak : Estropadak zerrenda. `year` eta `league` parametroak onartzen ditu.
    * /estropadak/<estropada_id>: Estropada emandako id-arentzat.
    * /sailkapenak: Sailkapen zerrenda.  `year` eta `league` parametroak onartzen ditu.
    * /emaitzak: Estropada emaitzen zerrenda. `year` eta `league` parametroak onartzen ditu.
    * /emaitzak/<estropada_id>: Estropada emaitza emandako id-arentzat.
    * /taldeak: Talde zerrenda.
    * /taldeak/<team>: Taldea emadako id-arentzat.
    * /estatistikak: Estatistika zerrenda.

# Tests

Just setup the env variables and run `pytest`.

Inguru aldagaiak ezarri eta `pytes` exekutatu.

```
$ COUCHDB=http://localhost:5984 DBNAME=estropadak pytest
```

# Contact / Harremana

You can contact me here or on Twitter (@estropadak).

Hemen edo Twitter bidez (@estropadak) nirekin harremanetan jar zaitezkete.