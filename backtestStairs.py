#####################################################
# Find first buy point, if Earn XX%, Sale, if Loss YY% buy same value
# Keep looping until sale all of Stock, Go back to Find buy point
#
#####################################################

import MySql as sql
import pandas as pd
import numpy as np
from datetime import datetime as dt
import datetime
from dateutil.relativedelta import *
import math
import time
import log
from collections import namedtuple


class BackTestStairs:
    ticker = ''
    start = dt.fromisoformat('2010-01-04')
    end = dt.today()
    initialCash = 30000
    takeProfit = 1.15
    coverUpBuy = 0.90

    dayPrice = []

    _TradeData = namedtuple('TradeData', 'dayId date openPrice highPrice lowPrice closePrice volume')

    def __init__(self):
        aa = sql.MySql()
        self.db = aa.dbconn()
        self.MyAcct = Account()
        self.MyAcct.initialValue = self.initialCash

    def loadDayPrice(self):
        dp = []

        runquery = self.db.cursor()
        query = 'SELECT dayId, date, openPrice, highPrice, lowPrice, closePrice, Volume ' \
                'FROM dayPrice WHERE code = %s AND Date > %s ORDER BY dayId'
        runquery.execute(query, tuple([self.ticker, self.start]))
        data = runquery.fetchall()
        for dayTradeData in data:
            a = self._TradeData(*dayTradeData)
            oneDayPrice = DayPrice()
            oneDayPrice.dayId = int(a.dayId)
            oneDayPrice.date = dt.date(a.date)
            oneDayPrice.openPrice = float(a.openPrice)
            oneDayPrice.highPrice = float(a.highPrice)
            oneDayPrice.lowPrice = float(a.lowPrice)
            oneDayPrice.closePrice = float(a.closePrice)
            oneDayPrice.volume = int(a.volume)
            self.dayPrice.append(oneDayPrice)

        # self.dayPrice = list(self.dayPrice)

    def initialBuyPoint(self, ticker, start):
        runquery = self.db.cursor()
        query = 'SELECT f_initialBuyPoint(%s , %s )'
        # f_initialBuyPoint
        dayId = 0
        runquery.execute(query, tuple([ticker, start]))
        results = runquery.fetchall()
        for result in results:
            print(result)
            if result:
                dayId = result[0]
            else:
                dayId = 0
            if not dayId:
                dayId = 0
        return dayId

    def startTrade(self, ticker, start):
        self.ticker = ticker
        self.start = start
        self.loadDayPrice()
        purchasePrice = []
        iniDayId = self.initialBuyPoint(ticker, start)
        for price in self.dayPrice:
            if int(price.dayId) < iniDayId:
                continue

            if price.dayId == iniDayId:
                # Do Buy
                self.MyAcct.buy(ticker, price.closePrice, price.date)
                continue

            ret, recentHold = self.MyAcct.recentHold(ticker)
            if ret == 0:
                iniDayId = self.initialBuyPoint(ticker, price.date)
                if iniDayId == 0:
                    break
                else:
                    continue
            else:
                # if up, sale
                if price.highPrice / recentHold.buyPrice > self.takeProfit:
                    # sale
                    tradePrice = max(price.lowPrice, price.openPrice, recentHold.buyPrice * self.takeProfit)
                    self.MyAcct.sale(ticker, tradePrice, price.date)

                if price.lowPrice / recentHold.buyPrice < self.coverUpBuy:
                    # if down buy
                    tradePrice = min(price.highPrice, price.openPrice, recentHold.buyPrice * self.coverUpBuy)
                    self.MyAcct.buy(ticker, tradePrice, price.date)

        self.evaluate()

    def evaluate(self):

        report = []
        report.append("Trade Start from: " + str(self.MyAcct.transactions[0].tradeDate))
        report.append("Trade end date: " + str(self.MyAcct.transactions[-1].tradeDate))
        report.append("Initial Value: " + str(self.MyAcct.initialValue))
        report.append("End Value: " + str(
            self.MyAcct.cash + sum(aHold.units for aHold in self.MyAcct.holds) * self.dayPrice[-1].closePrice))

        for a in report:
            print(a)

        for a in self.MyAcct.holds:
            print(a.buyDate, a.buyPrice, a.units)

        print("Buy/Sale", "Date", "Price", "Units", "Cash")
        for a in self.MyAcct.transactions:
            print(a.buySale, a.tradeDate, a.tradePrice, a.units, a.cash)
        # yearly performance
        # yearly equity performance

class Account:
    initialValue = 30000
    cash = initialValue
    holds = []
    transactionFee = 10
    transactions = []
    lastBuyPrice = 0.0
    currentPrice = 0.0

    def __init__(self):
        pass

    def buy(self, ticker, price, buyDate):
        if len(self.holds) < 5:
            amount = self.cash / (5 - len(self.holds))
            unit = math.floor(amount / price)
            self.cash = self.cash - unit * price - self.transactionFee
            newHold = Hold()
            newHold.ticker = ticker
            newHold.buyPrice = price
            newHold.units = unit
            newHold.buyDate = buyDate
            self.holds.append(newHold)

            newTrans = Transaction()
            newTrans.ticker = ticker
            newTrans.buySale = 'B'
            newTrans.units = unit
            newTrans.tradeDate = buyDate
            newTrans.tradePrice = price
            newTrans.cash = self.cash
            self.transactions.append(newTrans)

            return 1
        else:
            return 0

    def sale(self, ticker, price, saleDate):

        for aHold in reversed(self.holds):
            if aHold.ticker == ticker:
                self.cash = self.cash + aHold.units * price - self.transactionFee
                self.holds.remove(aHold)

                newTrans = Transaction()
                newTrans.ticker = ticker
                newTrans.buySale = 'S'
                newTrans.units = aHold.units
                newTrans.tradeDate = saleDate
                newTrans.tradePrice = price
                newTrans.cash = self.cash
                self.transactions.append(newTrans)
                return 1
                exit

        return 0

    def recentHold(self, ticker):
        for aHold in reversed(self.holds):
            if aHold.ticker == ticker:
                return 1, aHold

        return 0, Hold()


class Hold:
    ticker = ''
    buyPrice = 0.0
    buyDate = dt.today()
    units = 0


class Transaction:
    ticker = ''
    buySale = ''  # B(uy)S(ale)
    tradePrice = 0.0
    tradeDate = dt.today()
    units = 0
    cash = 0


class DayPrice:
    dayId = 0
    date = dt.today()
    openPrice = 0.0
    highPrice = 0.0
    lowPrice = 0.0
    closePrice = 0.0
    volume = 0


stair = BackTestStairs()
stair.startTrade('XQQ', dt.fromisoformat('2011-10-04'))
