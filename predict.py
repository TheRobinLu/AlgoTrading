import MySql as sql
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta


class Predict:
    tickers = []

    def __init__(self):
        self.mysql = sql.MySql()
        self.db = self.mysql.dbconn()

    def get_tickers(self):
        #get
        runquery = self.db.cursor()
        query = "SELECT code FROM equity WHERE active <> 'Y'"
        runquery.execute(query)

        result = runquery.fetchall()
        for a in result:
            self.tickers.append(''.join(a))

        return

    def pridict_by_day(self, date):
        runquery = self.db.cursor()
        self.get_tickers()

        for ticker in self.tickers:


            runquery.callproc("p_predict", tuple([ticker, date]))
            self.db.commit()
            print(dt.now(), "Completed p_predict for ", ticker)


    def top10_on_day(self, date):
        runquery = self.db.cursor()
        runquery.callproc("")
        self.db.commit()
        print(dt.now(), "Completed p_strategy_performance")



p = Predict()
day = dt.today()
#day = dt.fromisoformat("2022-04-28")
p.pridict_by_day(day)
