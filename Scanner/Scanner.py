import MySql as sql
from mysql.connector import Error
from collections import namedtuple
import datetime as dt

class Scanner:

    tickers = []
    results = []
    strategy = ''
    params = []
    date = dt.datetime.now()

    _Result = namedtuple('Result', 'code date demark')

    def __init__(self):
        self.SQL = sql.MySql()
        self.db = self.SQL.dbconn()

    def TickerList(self):
        self.tickers = self.SQL.get_tickers_id()
        pass

    def Parameter(self):
        self.params = []
        query = 'SELECT P.id FROM strategyparameters P, strategy S WHERE P.strategyId = S.id AND S.StrategyName = %s'
        runquery = self.db.cursor()
        runquery.execute(query, tuple([self.strategy]))
        data = runquery.fetchall()
        for a in data:
            self.params.append(a[0])
        print('Total Parameters:', len(self.params))
        return



    def Scan(self):
        print(dt.datetime.now())
        self.TickerList()
        pass

    def Sort(self):
        pass

    def Recommend(self):
        pass


