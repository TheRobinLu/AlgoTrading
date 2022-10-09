import yfinance as yf
from MySQLdb import IntegrityError

import MySql as sql
import pandas as pd
import numpy as np
from datetime import datetime as dt
import datetime
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
 #           self.calculateIndicators(tickerid)
        return

    def get_new(self, tickers):
        runquery = self.db.cursor()
        query = ''
        if len(tickers) == 0:
            tickers = self.get_tickers()
            if len(tickers) == 0:
                return

        for ticker in tickers:
            if ticker in ['EAAI.NE','EARK.NE']:
                self.get_hour([ticker])
                self.hour_day([ticker])
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
                lastDate = data[0][0] + datetime.timedelta(days=1)
                lastdayid = data[0][1]
                data = yf.download(ticker, start=lastDate)

            # if len(data) > 0:
            #     self.cleanuplast(tickerid, lastdayid)

            cnt = len(data)
            i = lastdayid + 1
            for date, market in data.iterrows():
                skip = 0
                for value in market:
                    if math.isnan(value):
                        skip = 1
                        break
                #if date <= lastDate:  a
                #    skip = 1

                if skip == 1:
                    continue

                #check if exi

                query = "INSERT INTO dayprice (code, dayId, date, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s FROM DUAL " \
                        "WHERE NOT EXISTS (SELECT 1 FROM dayprice WHERE code = %s AND date = %s)"
                #insert all
                row = []
                row.append(tickerid)
                row.append(i)
                a = str(date)
                row.append(a)
                row = row + market.to_list()
                row.append(tickerid)
                row.append(a)
                runquery.execute(query, tuple(row))
                self.db.commit()
                if runquery.rowcount > 0:
                    i = i+1
                    print("Importing ", tickerid, i, " of ", cnt)
            # ema
#            self.calculateIndicators(tickerid)

        return

    def get_hour(self, tickers):
        runquery = self.db.cursor()
        query = ''
        if len(tickers) == 0:
            tickers = self.get_tickers()
            if len(tickers) == 0:
                return

        for ticker in tickers:
            #get last date
            tickerid = self.get_tickerid(ticker, "yahoocode")
            query = "SELECT Max(date) as lastdate, Max(hourid) as lastdayid FROM hourprice WHERE code = '" + tickerid + "'"
            runquery.execute(query)
            data = runquery.fetchall()
            if data[0][0]==None:
                lastDate = dt.now() + datetime.timedelta(days=-729)
                lastdayid = 0
                data = yf.download(ticker, interval="1h", start=lastDate, group_by="ticker")
                #, start=lastDate

            else:
                lastDate = data[0][0]
                lastdayid = data[0][1]
                data = yf.download(ticker, interval="1h", start=lastDate, group_by="ticker")

            cnt = len(data)
            i = lastdayid + 1
            before = dt.now()
            seq = 0
            for date, market in data.iterrows():
                skip = 0
                for value in market:
                    if math.isnan(value):
                        skip = 1
                        break
                if skip == 1:
                    continue
                query = "INSERT INTO hourprice (code, hourId, date, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                #insert all
                if date == before:
                    seq = seq + 1
                else:
                    before = date
                    seq = 0
                date = self.sethour(date, seq)

                row = []
                row.append(tickerid)
                row.append(i)
                a = str(date)
                row.append(a)
                row = row + market.to_list()
                runquery.execute(query, tuple(row))
                self.db.commit()
                i = i+1
                print("Importing hour ", tickerid, i, " of ", cnt)


            # ema
            # self.calculateIndicators(tickerid)
            # calculate day price


        return

    def hour_day(self, tickers):
        runquery = self.db.cursor()
        query = ''
        if len(tickers) == 0:
            tickers = self.get_tickers()
            if len(tickers) == 0:
                return

        for ticker in tickers:
            # get last date
            tickerid = self.get_tickerid(ticker, "yahoocode")
            runquery.callproc("p_hour_day_price", tuple([tickerid]))
            self.db.commit()
            print("Convert hour price to day price for ", tickerid)


    def get_min(self, tickers, start, end):
        runquery = self.db.cursor()
        query = ''

        if start < dt.now() + relativedelta(days=-7):
            start = dt.now() + relativedelta(days=-7)

        if len(tickers) == 0:
            tickers = self.get_tickers()
            if len(tickers) == 0:
                return
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

                    print("Importing min ", tickerid, " for ", a)
                    self.db.commit()

        return

    def get_2min(self, tickers, start, end):
        runquery = self.db.cursor()
        query = ''

        if start < dt.now() + relativedelta(days=-7):
            start = dt.now() + relativedelta(days=-7)

        if len(tickers) == 0:
            tickers = self.get_tickers()
            if len(tickers) == 0:
                return
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
                    try:
                        runquery.execute(query, tuple(row))
                    except IntegrityError as err:
                        print('get a error')
                        pass

                    print("Importing 2mins ", tickerid, " for ", a)
                    self.db.commit()

        return

    def get_realtime(self, tickers, start):
        runquery = self.db.cursor()
        query = ''

        if start < dt.now() + relativedelta(days=-4):
            start = dt.now() + relativedelta(days=-4)

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
        select = "SELECT yahooCode FROM equity WHERE length(yahooCode) > 0  "
        # select = "SELECT yahooCode FROM equity WHERE length(yahooCode) > 0 " \
        #          "AND code not in (SELECT distinct code from RSI WHERE DaysInRange is not null) "
        cursor.execute(select)
        data = cursor.fetchall()
        tickers = []
        for a in data:
            tickers.append(''.join(a))
        return tickers


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
        query = "DELETE FROM demarkpoint WHERE code = %s AND dayid >= %s"
        runquery.execute(query, [ticker, dayid])
        self.db.commit()

    def cleanupToday(self):

        today = dt.today()
        runquery = self.db.cursor()

        query = "DELETE FROM dayprice WHERE date = %s"
        runquery.execute(query, [today])
        self.db.commit()

        query = "DELETE FROM ema WHERE date = %s"
        runquery.execute(query, [today])
        self.db.commit()

        query = "DELETE FROM kdj WHERE date = %s"
        runquery.execute(query, [today])

        self.db.commit()
        query = "DELETE FROM rsi WHERE date = %s"
        runquery.execute(query, [today])
        self.db.commit()

        query = "DELETE FROM bollinger WHERE date = %s"
        runquery.execute(query, [today])
        self.db.commit()

        query = "DELETE FROM demarkpoint WHERE date = %s"
        runquery.execute(query, [today])
        self.db.commit()



    def get_tickerid(self, ticker, codeType):
        runquery = self.db.cursor()
        query = "SELECT code FROM equity WHERE " + codeType + " = %s"
        runquery.execute(query, [ticker])

        return str(runquery.fetchone()[0])

    def sethour(self, date, seq):
        today = dt.today().replace(hour=0, minute=0, second=0, microsecond=0)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds = 95 * 360
        hour = date + datetime.timedelta(seconds=seconds + seq * 3600)
        return hour

    def get_duringDay(self, tickers):
        runquery = self.db.cursor()
        query = ''
        if len(tickers) == 0:
            tickers = self.get_tickers()
            if len(tickers) == 0:
                return
        self.cleanupToday()

        for ticker in tickers:
            if ticker in ['EAAI.NE','EARK.NE']:
                continue
            #get last date
            tickerid = self.get_tickerid(ticker, "yahoocode")
            query = "SELECT Max(dayid) as lastdayid FROM dayprice WHERE code = '" + tickerid + "'"
            runquery.execute(query)
            data = runquery.fetchall()
            if data[0][0]==None:
                continue
            else:
                lastDate = dt.today()
                lastdayid = data[0][1]
                data = yf.download(ticker, start=lastDate)

            cnt = len(data)
            i = lastdayid + 1
            for date, market in data.iterrows():
                skip = 0
                for value in market:
                    if math.isnan(value):
                        skip = 1
                        break
                #if date <= lastDate:  a
                #    skip = 1

                if skip == 1:
                    continue

                query = "INSERT INTO dayprice (code, dayId, date, openprice, highprice, lowprice, closeprice, adjclose, volume) "\
                        "SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s FROM DUAL " \
                        "WHERE NOT EXISTS (SELECT 1 FROM dayprice WHERE code = %s AND date = %s)"
                #insert all
                row = []
                row.append(tickerid)
                row.append(i)
                a = str(date)
                row.append(a)
                row = row + market.to_list()
                row.append(tickerid)
                row.append(a)
                runquery.execute(query, tuple(row))
                self.db.commit()
                if runquery.rowcount > 0:
                    i = i+1
                    print("Importing realtime dayprice", tickerid, " of today")
            # ema
        return

