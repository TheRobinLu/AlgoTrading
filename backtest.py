from typing import Union

import strategy as st
import datetime as dt
import MySql as sql
from collections import namedtuple
import math
import operator
import log


class BackTest:
    ticker = ""
    id = 0

    strategyParameters = []
    parameterId = 0
    strategyId = 0
    strategyName = ""
    parameter = [] ## parameter 1-8
    currentPara = ''

    TradeData = []
    start = dt.datetime.fromisoformat("2020-01-01")
    end = dt.datetime.fromisoformat("2020-01-01")

    startPrice = 0
    endPrice = 0
    startValue = 10000
    endValue = 10000
    TradeResults = []
    backTestDetail = []
    indicators = []



    _TradeData = namedtuple('TradeData', 'code dayId date close')
    _TradeDetail = namedtuple('TradeDetail', 'backTestId dayId date cash unit price balance status action')
    _TradeSummary = namedtuple('TradeSummary', 'parameterId code start end startPrice endPrice endValue')
    _Parameter = namedtuple('Parameter', 'strategyId Id intP1 intP2 intP3 intP4 decP5 decP6 decP7 decP8')

    def __init__(self):
        aa = sql.MySql()
        self.db = aa.dbconn()
        self.strategy = Strategy()
        self.currentPara = Parameter()
        self.log = log.Log()
        self.log.logfile = "backtest.log"
        self.highest = self.startValue

    def getStrategyId(self):
        if len(self.strategyName) > 0:
            runQuery = self.db.cursor()
            query = "SELECT id FROM strategy WHERE strategyName = %s"
            runQuery.execute(query, tuple([self.strategyName]))
            result = runQuery.fetchone()
            self.strategyId = result[0]
            return self.strategyId

    def getStrategy(self, strategyid):
        self.strategy.StrategyId = strategyid
        self.strategy.StrategyName = self.strategyName
        self.strategy.load()

    def getOneStrategy(self, ParameterId):
        runQuery = self.db.cursor()
        query = "SELECT ParameterId, intP1, intP2, intP3, intP4, decP1, decP2, decP3, decP4 " \
                "FROM strategyParameters WHERE ParameterId = %s"
        runQuery.execute(query, tuple([ParameterId]))
        result = runQuery.fetchone()
        for index, parameter in enumerate(result):
            self.parameter[index] = parameter

    def trade(self, inds):
        newResult = Result(self.start, self.end, self.currentPara)
        self.startPrice = inds[0].close
        for ind in inds:
            newDetail = Detail()
            #dayid, date, cash, unit, price, status, action)
            #newDetail.new(ind.dayId, ind.date, newResult.preDetail.cash, newResult.preDetail.unit, ind.price, '', '')

            if ind.buySale > 0:
                self.buy(ind, newResult)

            elif ind.buySale < 0:
                self.sale(ind, newResult)

            if newResult.preDetail.balance < self.startValue * 0.7:
                #discard
                self.log.infor("Discard for low absolute value for: " + self.ticker + "Parameter " +
                                    str(newResult.parameter.Id))
                return

            realtimeValue = newResult.preDetail.cash + newResult.preDetail.unit * ind.close
            profit = realtimeValue/self.startValue
            benchMark = ind.close / self.startPrice
            if profit < benchMark * 0.7:
                self.log.infor("Discard for low relative value for: " + self.ticker + "Parameter " +
                                    str(newResult.parameter.Id))
                return
        #set balance

        self.TradeResults.append(newResult)

    def buy(self, ind, result):
        newDetail = Detail()
        unit = 0
        if result.preDetail.unit > 0:
            if result.preDetail.cash / result.preDetail.balance < 0.1:
                StockPosition = 3
                return
            elif result.preDetail.cash / result.preDetail.balance < 0.4:
                StockPosition = 2
                if ind.buySale == 3:
                    # self.cash = self.cash + self.hold * ind.close
                    unit = math.floor(result.preDetail.cash / ind.close)
                    # all in
            else:
                StockPosition = 1
                if ind.buySale == 3:
                    # all in
                    unit = math.floor(result.preDetail.cash / ind.close)
                elif ind.buySale == 2:
                    # half of cash
                    unit = math.floor(result.preDetail.cash / (ind.close * 2))

        else:  # pre unit = 0
            StockPosition = 0
            unit = math.floor(result.preDetail.cash * ind.buySale / (ind.close * 3))

        if unit > 0:
            newDetail.cash = result.preDetail.cash - unit * ind.close
            newDetail.unit = result.preDetail.unit + unit
            newDetail.balance = newDetail.cash + newDetail.unit * ind.close
            newDetail.action = ind.buySale

            newDetail.dayId = ind.dayId
            result.details.append(newDetail)
            result.preDetail.cash = newDetail.cash
            result.preDetail.balance = newDetail.balance
            result.preDetail.unit = newDetail.unit


    def sale(self, ind, result):
        newDetail = Detail()
        unit = 0
        if result.preDetail.unit > 0:
            if result.preDetail.cash/result.preDetail.balance < 0.1:
               unit = math.floor(result.preDetail.unit * ind.buySale / (-3))
            if result.preDetail.cash / result.preDetail.balance < 0.4:
                if ind.buySale == -3:
                    unit = result.preDetail.unit
                elif ind.buySale == -2:
                    # sale half
                    unit = math.floor(result.preDetail.unit/2)
            elif result.preDetail.cash / result.preDetail.balance < 0.9:
                if ind.buySale == -3:
                    unit = result.preDetail.unit

            if unit > 0:
                newDetail.cash = result.preDetail.cash + unit * ind.close
                newDetail.unit = result.preDetail.unit - unit
                newDetail.balance = newDetail.cash + newDetail.unit * ind.close
                newDetail.action = ind.buySale

                newDetail.dayId = ind.dayId
                result.details.append(newDetail)
                result.preDetail.cash = newDetail.cash
                result.preDetail.balance = newDetail.balance
                result.preDetail.unit = newDetail.unit


    def evaluate(self):#TBD
        for result in self.TradeResults:
            result.endValue = result.details[-1].balance

        self.TradeResults.sort(key=operator.attrgetter('endValue'), reverse=True)

        maxCount = min(int(self.TradeResults.count/10), 1000)
        self.TradeResults = self.TradeResults[:maxCount]
        # select top 10%
        for result in self.TradeResults:
            self.saveResult(result)
        # ema * balance; amplify * balance
        return

    def saveResult(self, result): #TBD
        runQuery = self.db.cursor()
        #save summary
        query = "INSERT INTO backTestSummary (ParameterId, code, start, end, startPrice, endPrice, endValue) " \
                "VALUES (%s,%s,%s,%s,%s,%s,%s) "
        #save detail
        runQuery.execute(query, tuple([result.parameterId, self.ticker, result.start, result.end,
                                       result.startPrice, result.endPrice, result.endValue]))

        self.db.commit()
        #get backtestId
        for det in result.details:
            query = "INSERT INTO backTestDetail (ParameterId, code, start, end, startPrice, endPrice, endValue) " \
                    "VALUES (%s,%s,%s,%s,%s,%s,%s) "
            # runQuery.execute(query, tuple[])

class Result:
    backtestId = 0

    code = ''
    start = dt.datetime.fromisoformat("2020-01-01")
    end = dt.datetime.fromisoformat("2020-01-01")
    startPrice = 0
    endPrice = 0
    startValue = 10000
    endValue = 10000
    details = []

    def __init__(self, start, end, parameter):

        self.start = start
        self.end = end
        self.parameter = parameter
        self.details = []
        self.details.append(Detail())
        self.preDetail = Detail()
        self.preDetail.cash = self.startValue
        self.preDetail.balance = self.startValue
        self.preDetail.tradeDate = start
        # detail.cash = self.startValue
        # detail.balance = self.startValue
        # detail.tradeDate = start
        # self.details.append(detail)

    def save(self):
        aa = sql.MySql()
        db = aa.dbconn()

        db.disconnect()
        pass


class Detail:
    tradeDate = dt.datetime.fromisoformat("2020-01-01")
    backtestId = 0
    dayId = 0
    cash = 0
    unit = 0
    price = 0
    balance = 0
    status = ""
    action = ""

    def __init__(self):
        pass

    def new(self, dayid, date, cash, unit, price, status, action):
        self.dayId = dayid
        self.tradeDate = date
        self.cash = cash
        self.unit = unit
        self.price = price
        self.status = status
        self.action = action

    # def trade(self, buyPoint, ind, results):
    #     if buyPoint > 0:
    #         self.buy(buyPoint, ind, results)
    #     elif buyPoint < 0:
    #         self.sale(buyPoint, ind, results)
    #
    # def buy(self, buyPoint, ind, results): # 1-3
    #     StockPosition = 0
    #     unit = 0
    #     if results.preDetail.unit > 0:
    #         if results.preDetail.cash/ results.preDetail.balance < 0.1:
    #             StockPosition = 3
    #             return
    #         elif results.preDetail.cash / results.preDetail.balance < 0.4:
    #             StockPosition = 2
    #             if buyPoint == 3:
    #                 #self.cash = self.cash + self.hold * ind.close
    #                 unit = math.floor(results.preDetail.cash / ind.close)
    #                 #all in
    #         else:
    #             StockPosition = 1
    #             if buyPoint == 3:
    #                 # all in
    #                 unit = math.floor(results.preDetail.cash / ind.close)
    #             elif buyPoint == 2:
    #                 # half of cash
    #                 unit = math.floor(results.preDetail.cash / (ind.close * 2))
    #
    #     else: # pre unit = 0
    #         StockPosition = 0
    #         unit = math.floor(results.preDetail.cash * buyPoint / (ind.close * 3))
    #
    #     self.cash = results.preDetail.cash - unit * ind.close
    #     self.unit = results.preDetail.unit + unit
    #     self.balance = self.cash + self.unit * ind.close
    #     self.action = buyPoint
    #
    #     self.dayId = ind.dayId
    #     results.append(self)
    #     results.preDetail.cash = self.cash
    #     results.preDetail.balance = self.balance
    #     results.preDetail.unit = self.unit
    #
    # def sale(self, buyPoint, ind, results):
    #     unit = 0
    #     if results.preDetail.unit > 0:
    #         if results.preDetail.cash/results.preDetail.balance < 0.1:
    #            unit = math.floor(results.preDetail.unit * buyPoint / (-3))
    #         if results.preDetail.cash / results.preDetail.balance < 0.4:
    #             if buyPoint == -3:
    #                 unit = results.preDetail.unit
    #             elif buyPoint == -2:
    #                 # sale half
    #                 unit = math.floor(results.preDetail.unit/2)
    #         elif results.preDetail.cash / results.preDetail.balance < 0.9:
    #             if buyPoint == -3:
    #                 unit = results.preDetail.unit
    #
    #     self.cash = results.preDetail.cash + unit * ind.close
    #     self.unit = results.preDetail.unit - unit
    #     self.balance = self.cash + self.unit * ind.close
    #     self.action = buyPoint
    #
    #     self.dayId = ind.dayId
    #     results.append(self)
    #     results.preDetail.cash = self.cash
    #     results.preDetail.balance = self.balance
    #     results.preDetail.unit = self.unit
    #
    #     return

    def save(self):

        self.db = sql.MySql().dbconn()
        runQuery = self.db.cursor()
        query = "INSERT INTO backTestDetail (backtestId, dayid, date, cash, unit, Price, status, action) " \
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "

        runQuery.execute(query, tuple([self.backtestId, self.dayId, self.tradeDate, self.cash, self.unit, self.price,
                                      self.status, self.action]))

        self.db.commit()
        self.db.disconnect()

class TradeData:
    def __init__(self):
        self.code = ""
        self.dayId = 0
        self.date = dt.datetime.fromisoformat("2020-01-01")
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.Volume = 0

    def new(self, code, dayId, date, open, high, low, close, Volume ):
        self.code = code
        self.dayId = dayId
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.Volume = Volume


class Parameter:
    def __init__(self):
        self.strategyId = 0
        self.Id = 0
        self.intP1 = 0
        self.intP2 = 0
        self.intP3 = 0
        self.intP4 = 0
        self.decP5 = 0
        self.decP6 = 0
        self.decP7 = 0
        self.decP8 = 0

    def new(self, strategyId, Id, intP1, intP2, intP3, intP4, decP5, decP6, decP7, decP8):
        self.strategyId = strategyId
        self.Id = Id
        self.intP1 = intP1
        self.intP2 = intP2
        self.intP3 = intP3
        self.intP4 = intP4
        self.decP5 = decP5
        self.decP6 = decP6
        self.decP7 = decP7
        self.decP8 = decP8


class Strategy:
    def __init__(self):
        aa = sql.MySql()
        self.db = aa.dbconn()
        self.StrategyName = ""
        self.StrategyId = 0
        self.Parameters = []

    def load(self):
        runQuery = self.db.cursor()
        query = "SELECT strategyId, Id, intP1, intP2, intP3, intP4, decP5, decP6, decP7, decP8 " \
                "FROM strategyParameters WHERE strategyId = %s "\
                " AND intP2 = intP3 AND decP6 = 1"
        runQuery.execute(query, tuple([self.StrategyId]))
        results = runQuery.fetchall()
        a = namedtuple('Parameter', 'strategyId Id intP1 intP2 intP3 intP4 decP5 decP6 decP7 decP8')
        for result in results:
            p = a(*result)
            newParameter = Parameter()
            newParameter.new(p.strategyId, p.Id, p.intP1, p.intP2, p.intP3, p.intP4, p.decP5,
                             p.decP6, p.decP7, p.decP8)

            self.Parameters.append(newParameter)


    # _TradeDetail = namedtuple('TradeDetail', 'backTestId dayId date cash unit price balance status action')
    # _TradeSummary = namedtuple('TradeSummary', 'parameterId code start end startPrice endPrice endValue')


class Indicator:
    code = ''
    dayId = 0
    date = dt.datetime.fromisoformat("2020-01-01")
    close = 0.1
    emadays = 0
    deviation = 0.1
    ema = 0
    trend = 0
    short = 0
    position = 0
    buySale = 0
    status = ''
    strategy = ''

    def __init__(self):
        self.parameter = Parameter()


    def new(self, code, dayid, date, close, emadays, deviation, ema, trend, short):
        self.code = code
        self.dayId = dayid
        self.date = date
        self.close = close
        self.emadays = emadays
        self.deviation = deviation
        self.ema = ema
        self.trend = trend
        self.short = short



