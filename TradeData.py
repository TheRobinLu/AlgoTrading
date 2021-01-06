import yfinance as yf
import MySql as sql
import pandas as pd
import numpy as np
from datetime import datetime as dt
from dateutil.relativedelta import *
import math
import time


class TradeData:

    def __init__(self):
        aa = sql.MySql()
        self.db = aa.dbconn()

    def get_all(self, tickers):
        runquery = self.db.cursor()
        query = ''
        if len(tickers) == 0:
            tickers = self.get_tickers()

        for ticker in tickers:
            print("starting import ", ticker)
            tickerid = self.get_tickerid(ticker, "yahoocode")
            data = yf.download(ticker)
            if len(data) > 0:
                # delete history data
                query = "p_removehistory"
                runquery.callproc(query, [tickerid])
                self.db.commit()
            #insert to
            cnt = len(data)
            i = 1
            for date, market in data.iterrows():
                skip = 0
                for value in market:
                    if math.isnan(value):
                        skip = 1
                        break
                if skip == 1:
                    continue
                query = "INSERT INTO dayprice (code, dayId, date, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                #insert all
                row = []
                row.append(tickerid)
                row.append(i)
                a = str(date)
                row.append(a)
                row = row + market.to_list()
                runquery.execute(query, tuple(row))
                self.db.commit()
                print("Importing", tickerid, i, " of ", cnt)
                i = i+1

            # 3 days ema
            self.calculateIndicators(tickerid)
        return

    def get_new(self, tickers):
        runquery = self.db.cursor()
        query = ''
        if len(tickers) == 0:
            tickers = self.get_tickers()

        for ticker in tickers:
            if ticker in ['EAAI.NE','EARK.NE']:
                self.get_hour([ticker])
                continue
            #get last date
            tickerid = self.get_tickerid(ticker, "yahoocode")
            query = "SELECT Max(date) as lastdate, Max(dayid) as lastdayid FROM dayprice WHERE code = '" + tickerid + "'"
            runquery.execute(query)
            data = runquery.fetchall()
            if data[0][0]==None:
                lastDate = dt.strptime("1950-01-01", "%Y-%m-%d")
                lastdayid = 0
                data = yf.download(ticker)

            else:
                lastDate = data[0][0]
                lastdayid = data[0][1]
                data = yf.download(ticker, start=lastDate)

            if len(data) > 0:
                self.cleanuplast(tickerid, lastdayid)

            cnt = len(data)
            i = lastdayid
            for date, market in data.iterrows():
                skip = 0
                for value in market:
                    if math.isnan(value):
                        skip = 1
                        break
                if skip == 1:
                    continue
                query = "INSERT INTO dayprice (code, dayId, date, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                #insert all
                row = []
                row.append(tickerid)
                row.append(i)
                a = str(date)
                row.append(a)
                row = row + market.to_list()
                runquery.execute(query, tuple(row))
                self.db.commit()
                i = i+1
                print("Importing ", tickerid, i, " of ", cnt)
            # ema
            self.calculateIndicators(tickerid)

        return

    def get_hour(self, tickers):
        runquery = self.db.cursor()
        query = ''
        if len(tickers) == 0:
            tickers = self.get_tickers()

        for ticker in tickers:
            #get last date
            tickerid = self.get_tickerid(ticker, "yahoocode")
            query = "SELECT Max(date) as lastdate, Max(dayid) as lastdayid FROM dayprice WHERE code = '" + tickerid + "'"
            runquery.execute(query)
            data = runquery.fetchall()
            if data[0][0]==None:
                lastDate = dt.strptime("2019-01-05", "%Y-%m-%d")
                lastdayid = 0
                data = yf.download(ticker, interval="1h", start=lastDate, group_by="ticker")
                #, start=lastDate

            else:
                lastDate = data[0][0]
                lastdayid = data[0][1]
                data = yf.download(ticker, start=lastDate)

            if len(data) > 0:
                self.cleanuplast(tickerid, lastdayid)

            cnt = len(data)
            i = lastdayid
            for date, market in data.iterrows():
                skip = 0
                for value in market:
                    if math.isnan(value):
                        skip = 1
                        break
                if skip == 1:
                    continue
                query = "INSERT INTO dayprice (code, dayId, date, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                #insert all
                row = []
                row.append(tickerid)
                row.append(i)
                a = str(date)
                row.append(a)
                row = row + market.to_list()
                runquery.execute(query, tuple(row))
                self.db.commit()
                i = i+1
                print("Importing ", tickerid, i, " of ", cnt)
            # ema
            # self.calculateIndicators(tickerid)

        return

    def get_min(self, tickers, start, end):
        runquery = self.db.cursor()
        query = ''

        if start < dt.now() + relativedelta(days=-7):
            start = dt.now() + relativedelta(days=-7)

        if len(tickers) == 0:
            tickers = self.get_tickers()

        str_tickers = ' '.join(tickers)
        data = yf.download(str_tickers, interval="1m", start=start, group_by="ticker")

        for ticker in tickers:
            tickerid = self.get_tickerid(ticker, "yahoocode")
            if len(data[ticker]) > 0:
                #clean up min
                #query = "DELETE FROM minprice WHERE code ='{0}' AND tradeTime between '{1}' and '{2}'"
                #query = query.format(arg[0], arg[1], arg[2])
                #runquery.execute(query)
                query = "DELETE FROM minprice WHERE code =%s AND tradeTime between %s and %s"
                arg = [tickerid, start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")]
                runquery.execute(query, tuple(arg))
                self.db.commit()

                for time, market in data[ticker].iterrows():
                    skip = 0
                    for value in market:
                        if math.isnan(value):
                            skip = 1
                            break
                    if skip == 1:
                        continue
                    row = []
                    query = "INSERT INTO minprice (code, tradeTime, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                    row.append(tickerid)
                    a = str(time)
                    row.append(a)
                    row = row + market.to_list()
                    runquery.execute(query, tuple(row))

                    print("Importing ", tickerid, " for ", a)
                    self.db.commit()

        return

    def get_2min(self, tickers, start, end):
        runquery = self.db.cursor()
        query = ''

        if start < dt.now() + relativedelta(days=-7):
            start = dt.now() + relativedelta(days=-7)

        if len(tickers) == 0:
            tickers = self.get_tickers()

        str_tickers = ' '.join(tickers)
        data = yf.download(str_tickers, interval="2m", start=start,  group_by="ticker")

        for ticker in tickers:
            tickerid = self.get_tickerid(ticker, "yahoocode")
            if len(data[ticker]) > 0:
                #clean up min
                #query = "DELETE FROM minprice WHERE code ='{0}' AND tradeTime between '{1}' and '{2}'"
                #query = query.format(arg[0], arg[1], arg[2])
                #runquery.execute(query)
                query = "DELETE FROM min2price WHERE code =%s AND tradeTime between %s and %s"
                arg = [tickerid, start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")]
                runquery.execute(query, tuple(arg))
                self.db.commit()

                for time, market in data[ticker].iterrows():
                    skip = 0
                    for value in market:
                        if math.isnan(value):
                            skip = 1
                            break
                    if skip == 1:
                        continue
                    row = []
                    query = "INSERT INTO min2price (code, tradeTime, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                    row.append(tickerid)
                    a = str(time)
                    row.append(a)
                    row = row + market.to_list()
                    runquery.execute(query, tuple(row))

                    print("Importing ", tickerid, " for ", a)
                    self.db.commit()

        return

    def get_realtime(self,tickers, start):
        runquery = self.db.cursor()
        query = ''

        if start < dt.now() + relativedelta(days=-7):
            start = dt.now() + relativedelta(days=-7)

        if len(tickers) == 0:
            tickers = self.get_tickers()

        str_tickers = ' '.join(tickers)
        data = yf.download(str_tickers, interval="1m", start=start, group_by="ticker")

        for ticker in tickers:
            if len(data[ticker]) > 0:
                query = "DELETE FROM realtime WHERE code =%s AND tradeTime > %s"
                arg = [ticker, start.strftime("%Y-%m-%d %H:%M:%S")]
                runquery.execute(query, tuple(arg))
                self.db.commit()
                for time, market in data[ticker].iterrows():
                    if math.isnan(market[0]):
                        continue
                    row = []
                    query = "SELECT Max(tradeTime) FROM realtime WHERE code = %s"
                    runquery.execute(query, tuple(ticker))
                    maxTime = runquery.fetchall()
                    if time < maxTime:
                        continue

                    query = "INSERT INTO realtime (code, tradeTime, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                    row.append(ticker)
                    a = str(time)
                    row.append(a)
                    row = row + market.to_list()
                    runquery.execute(query, tuple(row))
                    self.db.commit()
                    print(row)
        return

    def monitor(self, tickers):

        tradingstart = dt.strptime("2000-01-01 09:30:00", "%Y-%m-%d %H:%M:%S").time()
        tradingend = dt.strptime("2000-01-01 16:00:00", "%Y-%m-%d %H:%M:%S").time()
        print(dt.now().time())
        while dt.now().time() <= tradingend:
            if dt.now().time() < tradingstart:
                continue
            self.get_realtime(tickers, dt.now() + relativedelta(seconds=-125))
            print(dt.now())
            time.sleep(10)

    def get_tickers(self):
        cursor = self.db.cursor()
        select = "SELECT yahooCode FROM equity WHERE length(yahooCode) > 0"
        cursor.execute(select)
        data = cursor.fetchall()
        tickers = []
        for a in data:
            tickers.append(''.join(a))
        return tickers

    def calculateIndicators(self, ticker):
        emadays = [3,5,7,10,12,14,15,16,20,25,26,30,40,50,70,90,120,150,180,240]
        runquery = self.db.cursor()
        for day in emadays:
            runquery.callproc('p_ema', [ticker, day])
            print("Calculate EMA ", ticker, day)

        return

    def calculateRSI(self, ticker):
        emadays = [3,5,7,10,12,14,15,16,20,25,26,30,40,50,70,90,120,150,180,240]
        runquery = self.db.cursor()
        for day in emadays:
            runquery.callproc('p_ema', [ticker, day])
            print("Calculate EMA ", ticker, day)

        return

    def cleanupall(self, ticker):
        runquery = self.db.cursor()
        query = "DELETE FROM dayprice WHERE code = %s"
        runquery.execute(query, [ticker])
        query = "DELETE FROM ema WHERE code = %s"
        runquery.execute(query, [ticker])
        query = "DELETE FROM kdj WHERE code = %s"
        runquery.execute(query, [ticker])
        query = "DELETE FROM rsi WHERE code = %s "
        runquery.execute(query, [ticker])
        query = "DELETE FROM bollinger WHERE code = %s"
        runquery.execute(query, [ticker])
        self.db.commit()

    def cleanuplast(self, ticker, dayid):
        runquery = self.db.cursor()
        query = "DELETE FROM dayprice WHERE code = %s AND dayid >= %s"
        runquery.execute(query, [ticker, dayid])
        query = "DELETE FROM ema WHERE code = %s AND dayid >= %s"
        runquery.execute(query, [ticker, dayid])
        query = "DELETE FROM kdj WHERE code = %s AND dayid >= %s"
        runquery.execute(query, [ticker, dayid])
        query = "DELETE FROM rsi WHERE code = %s AND dayid >= %s"
        runquery.execute(query, [ticker, dayid])
        query = "DELETE FROM bollinger WHERE code = %s AND dayid >= %s"
        runquery.execute(query, [ticker, dayid])
        self.db.commit()

    def get_tickerid(self, ticker, codeType):
        runquery = self.db.cursor()
        query = "SELECT code FROM equity WHERE " + codeType + " = %s"
        runquery.execute(query, [ticker])

        return str(runquery.fetchone()[0])

