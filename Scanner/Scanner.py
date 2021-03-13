import MySql as sql
from mysql.connector import Error
from collections import namedtuple

class Scanner:

    tikers = []
    results = []

    _Result = namedtuple('Result', 'code date demark')

    def __init__(self):
        self.SQL = sql.MySql()
        self.db = self.SQL.dbconn()

    def TickerList(self):
        self.tickers = self.SQL.get_tickers_id()
        pass

    def Scan(self):
        pass

    def Sort(self):
        pass

    def Recommend(self):
        pass

