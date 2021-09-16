import backtest
import MySql as sql
from mysql.connector import Error
import datetime as dt
from collections import namedtuple
from operator import attrgetter
import decimal



class BackTestBollinger(backtest.BackTest):
    emaDay = 0
    demaDays = 0
    short = 0
    amplify = 0
    demaAmp = 0
    TrainStart = dt.datetime.fromisoformat("2020-01-01")
    TrainEnd = dt.datetime.fromisoformat("2020-01-01")
    TestStart = dt.datetime.fromisoformat("2020-01-01")
    TestEnd = dt.datetime.fromisoformat("2020-01-01")
    BollParameters = []


    _BollParameter = namedtuple('BollParameter', 'strategyId ParameterId emadays trend short amplify shortAmplify')
    _Indicator = namedtuple('Indicator', 'code dayid date close emadays deviation ema trend short')
    _TradeDataBoll = namedtuple('TradeDataBollinger', 'code dayid date close emadays deviation ema trend short')

    def __init__(self):
        super().__init__()
        self.strategyName = "Bollinger"
        aa = sql.MySql()
        self.db = aa.dbconn()
        self.BollStrategy = BollingerStrategy()

    def getStrategy(self, strategyid):
        super().getStrategy(strategyid)
        self.strategy.strategyName = self.strategyName

        self.BollStrategy.StrategyId = self.strategy.StrategyId
        self.BollStrategy.StrategyName = self.strategy.strategyName
        for p in self.strategy.Parameters:
            bp = BollingerParameter()
            bp.new(p.strategyId, p.Id, p.intP1, p.intP2, p.intP3, p.intP4, p.decP5, p.decP6, p.decP7, p.decP8)
            self.BollStrategy.bollParameters.append(bp)

    def Training(self):
        preShort = -1

        for parameter in self.BollStrategy.bollParameters:
            self.currentPara = parameter
            newResult = backtest.Result(self.TrainStart, self.TrainEnd, parameter)
            # newResult.details.append(backtest.Detail())

            #retrieve Trade Data
            if parameter.short != preShort:
                self.getTradeInfor(parameter, self.TrainStart, self.TrainEnd)
                preShort = parameter.short

            self.buySale(parameter)

            #self.log.infor("Complete Buy Sale setup for " + str(parameter.Id))
            self.TradeResults.append(newResult)

        self.evaluate(self.TradeResults) # filter out bad parameter

        self.saveResult()
        # for result in self.TradeResults:
        #     result.save()

    def setDate(self, trainStart, trainEnd, testStart, testEnd):
        #
        self.TrainStart = trainStart
        self.TrainEnd = trainEnd
        self.TestStart = testStart
        self.TestEnd = testEnd

    def setRetrieveParameter(self, parameter):

        return self._BollParameter(parameter.strategyId, parameter.Id, parameter.intP1,
                                   parameter.intP2, parameter.intP3, parameter.decP5, parameter.decP6)


    def getTradeInfor(self, parameter, start, end):
        runquery = self.db.cursor()
        runquery.callproc("p_bollinger_trend", tuple([self.ticker, parameter.emadays, parameter.trend, parameter.short,
                                                      start, end]))
        for result in runquery.stored_results():
            self.TradeData = result.fetchall()

#         code dayid date close emadays deviation ema trend(dema) short(sdema)
        for dayTrade in self.TradeData:
            a = self._Indicator(*dayTrade)
            self.indicators.append(a)


    def buySale(self, parameter):
        BuyPoint = 0 # 2, 1, 0, -1, -2
        detail = backtest.Detail()
        detail.tradeDate = self.start
        dayId = 0
        cash = 0
        unit = 0
        price = 0
        balance = 0
        status = ""
        action = ""

        stockIndicators = []

        for ind in self.indicators:
            #code dayid date close emadays deviation ema trend short
            # prePosition
            newIndicator = backtest.Indicator()
            newIndicator.new(ind.code, ind.dayid, ind.date, ind.close, ind.emadays, ind.deviation, ind.ema,
                            ind.trend, ind.short)

            newIndicator.position = 0
            newIndicator.buySale = 0

            status = ""
            upband = ind.ema + ind.deviation * float(parameter.amplify) + \
                     ind.trend * float(parameter.shortAmplify)
            lowband = ind.ema - ind.deviation * float(parameter.amplify) + \
                     ind.trend * float(parameter.shortAmplify)
            # dayTrade.append([upband, lowband])
            if ind.close < lowband * 0.92:
                newIndicator.position = -3
                newIndicator.buySale = 3
            elif ind.close < lowband:
                newIndicator.position = -2
                newIndicator.buySale = 2
            elif ind.close < ind.ema:
                newIndicator.position = -1
                if ind.short/ind.ema > 0.002:
                    newIndicator.buySale = 1
                elif ind.short/ind.ema < -0.002: #May need remove
                    newIndicator.buySale = -1
            elif ind.close < upband:
                newIndicator.position = -1
                if ind.short/ind.ema > 0.002:#May need remove
                    newIndicator.buySale = 1
                elif ind.short/ind.ema < -0.002:
                    newIndicator.buySale = -1
            elif ind.close < upband * 1.1:
                newIndicator.position = 2
                newIndicator.buySale = -2
            else:
                newIndicator.position = 3
                newIndicator.buySale = -3

            stockIndicators.append(newIndicator)

        self.log.infor("Complete Buy Sale setup for " + str(parameter.Id))

        #self.trade(stockIndicators)


class BollingerParameter(backtest.Parameter):
    def __init__(self):
        super().__init__()
        self.emadays = 0
        self.trend = 0
        self.short = 0
        self.amplify = 0
        self.shortAmplify = 0

    def new(self, strategyId, Id, intP1, intP2, intP3, intP4, decP5, decP6, decP7, decP8):
        super().new(strategyId, Id, intP1, intP2, intP3, intP4, decP5, decP6, decP7, decP8)
        self.emadays = intP1
        self.trend = intP2
        self.short = intP3
        self.amplify = decP5
        self.shortAmplify = decP6


class BollingerStrategy(backtest.Strategy):
    def __init__(self):
        super().__init__()
        self.bollParameters = []

    def load(self):
        super().load()
        for p in self.Parameters:
            bp = BollingerParameter()
            bp.new(p.strategyId, p.Id, p.intP1, p.intP2, p.intP3, p.intP4, p.decP5, p.decP6, p.decP7, p.decP8)
            self.bollParameters.append(bp)






