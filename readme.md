# estropadak-flask-restful

flask-restful implementation of estropadak REST API

# Enpoints

    * /estropadak/<league>/<year> : Return list of estropadak for given league and year
    * /estropada/<estropada_id>: Return estropada data for given id
    * /sailkapena/<league_id>/<year>: Return rank for given league and year
    * /sailkapena/<league_id>/<year>/<team>: Return rank for given team in league and year

# Tests
```
python estropadak_test.py
```