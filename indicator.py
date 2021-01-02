import MySql as sql
from datetime import datetime as dt
from dateutil.relativedelta import *
import time


class Indicator:

    def __init__(self):
        self.mysql = sql.MySql()
        self.db = self.mysql.dbconn()

    def ema(self):
        tickers = self.mysql.get_tickers_id()
        for ticker in tickers:
            self.ema(self,ticker)

    def rsi(self):
        tickers = self.mysql.get_tickers_id()
        for ticker in tickers:
            self.rsi(self,ticker)

    def kdj(self):
        tickers = self.mysql.get_tickers_id()
        for ticker in tickers:
            self.kdj(self,ticker)

    def bollinger(self):
        return

    def ema(self, ticker):
        emadays = [3, 5, 7, 10, 12, 14, 15, 16, 20, 25, 26, 30, 40, 50, 70, 90, 120, 150, 180, 240]
        for day in emadays:
            self.ema(ticker,day)

    def ema(self, ticker, day):
        runquery = self.db.cursor()
        runquery.execute("p_ema", [ticker, day])

    def rsi(self, ticker):
        self.rsi (ticker, 7)
        self.rsi (ticker, 14)
        self.rsi (ticker, 21)


    def rsi(self, ticker, day):
        runquery = self.db.cursor()
        runquery.execute("p_rsi", [ticker, day])

    def kdj(self, ticker):
        days = [5,6,9,18,19,34,36,45,55,73,89]
        for day in days:
            self.kdj(ticker, day)


    def kdj(self, ticker, day):
        runquery = self.db.cursor()
        runquery.execute("p_rsi", [ticker, day, 3])

