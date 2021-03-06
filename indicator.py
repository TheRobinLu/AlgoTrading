import MySql as sql
from datetime import datetime as dt
from dateutil.relativedelta import *
import time


class Indicator:

    def __init__(self):
        self.mysql = sql.MySql()
        self.db = self.mysql.dbconn()

    def ema(self, tickers=[], emadays=[3, 5, 7, 10, 12, 14, 15, 16, 20, 25, 26, 30, 40, 50, 70, 90, 120, 150, 180, 240]):
        runquery = self.db.cursor()
        if len(tickers) == 0:
            tickers = self.mysql.get_tickers_id()
        for ticker in tickers:
            for day in emadays:
                runquery.callproc("p_ema", tuple([ticker, day]))
                self.db.commit()
                print("Completed EMA for ", ticker, day)

    def rsi(self, tickers=[], days=[7, 14, 21]):
        runquery = self.db.cursor()
        if not tickers:
            tickers = self.mysql.get_tickers_id()
        for ticker in tickers:
            for day in days:
                runquery.callproc("p_rsi", tuple([ticker, day]))
                self.db.commit()
                print("Completed RSI for ", ticker, day)

    def kdj(self, tickers=[], days=[5,6,9,18,19,34,36,45,55,73,89]):
        runquery = self.db.cursor()
        if not tickers:
            tickers = self.mysql.get_tickers_id()

        for ticker in tickers:
            for day in days:
                runquery.callproc("p_kdj", tuple([ticker, day, 3]))
                self.db.commit()
                print("Completed KDJ for ", ticker, day)

    def bollinger(self):
        return


