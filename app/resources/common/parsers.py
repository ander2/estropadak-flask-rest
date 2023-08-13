from ...config import LEAGUES, PAGE_SIZE
from flask_restx import reqparse

league_year_parser = reqparse.RequestParser()
league_year_parser.add_argument('league', type=str, choices=LEAGUES, case_sensitive=False, required=False)
league_year_parser.add_argument('year', type=int, required=False)
league_year_parser.add_argument('page', type=int, help="Page number", default=0, required=False)
league_year_parser.add_argument('count', type=int, help="Elements per page", default=PAGE_SIZE, required=False)

required_league_year_parser = reqparse.RequestParser()
required_league_year_parser.add_argument('league',
                                         type=str, choices=LEAGUES,
                                         case_sensitive=False, required=True)
required_league_year_parser.add_argument('year', type=int, required=False)
required_league_year_parser.add_argument('category', type=str, required=False)


estatistikak_parser = reqparse.RequestParser()
estatistikak_parser.add_argument('league', type=str, required=True, choices=LEAGUES, case_sensitive=False)
estatistikak_parser.add_argument('year', type=int)
estatistikak_parser.add_argument('team', type=str)
estatistikak_parser.add_argument('category', type=str)
estatistikak_parser.add_argument('stat', type=str, default='cumulative')

emaitzak_parser = reqparse.RequestParser()
emaitzak_parser.add_argument('criteria', type=str, case_sensitive=True, required=True, help="Search criteria")
emaitzak_parser.add_argument('page', type=int, help="Page number", default=0)
emaitzak_parser.add_argument('count', type=int, help="Elements per page", default=PAGE_SIZE)