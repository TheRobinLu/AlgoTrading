import MySql as sql
from mysql.connector import Error
import math


class Strategy:
    def __init__(self):
        aa = sql.MySql()
        self.db = aa.dbconn()
        self.balance = []
        self.cash = 10000
        self.value = 10000
        self.hold = 0
        self.transaction = 10
        return

    def bollinger_trend(self, tickers, start):
        # lower than low band --> buy
        # higher than upper band --> sale
        # Loop tickers
        summaryfile = "D:\\backtest\\bollinger\\sum.txt"
        for ticker in tickers:
            # initial 10000, 10 transaction fee
            runquery = self.db.cursor()

            #days = [20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38]
            # loop days  10 - 30
            for day in range(28, 40):
                # loop amplify of deviation 1.0 - 3.0
                for amplify in range(25, 30, 1):
                    amplify = amplify/10
                    parameter = []
                    parameter.append(ticker)
                    parameter.append(day)
                    parameter.append(amplify)
                    parameter.append(start)
                    try:
                        args = runquery.callproc('p_bollinger', tuple(parameter))
                    except Error as e:
                        print(e)
                        return

                    for result in runquery.stored_results():
                        bollinger = result.fetchall()

                    # bollinger structure: code,dayid,days,amplify,Deviation,closeprice,ema,dema,upper,lower
                    # loop trend 0 - 2
                    for trend in range(8, 25, 1):
                        #adjust band
                        trend = trend/10
                        print(ticker, day, amplify, trend)
                        self.cash = 10000
                        self.hold = 0
                        self.value = 10000
                        self.balance = []
                        for daybollinger in bollinger:
                            #check if total balance < 6666 stop test
                            if self.cash + self.hold * daybollinger[5] < 6666:
                                break

                            if self.hold > 0 and daybollinger[5] > daybollinger[8] + \
                                    trend * daybollinger[7]:
                                #sell
                                self.cash = self.cash + self.hold * daybollinger[5] - self.transaction
                                self.hold = 0

                            if self.hold == 0 and daybollinger[5] < daybollinger[9] + \
                                    trend * daybollinger[7]:
                                #buy
                                unit = math.floor(self.cash / daybollinger[5])
                                self.hold = unit
                                self.cash = self.cash - unit * daybollinger[5] - self.transaction

                            self.value = self.cash + self.hold * daybollinger[5]
                            self.balance.append([ticker, daybollinger[1], daybollinger[5], self.cash, self.hold, self.value])

                        filename = "D:\\backtest\\bollinger\\" + ticker + '-ema' + str(day) + '-amplify' + str(amplify) +\
                                                                    '-trend' + str(trend) + '.txt'

                        f = open(filename, "w")
                        for bal in self.balance:
                            f.write(str(bal) + "\n")

                        f.close()

                        s = open(summaryfile, "a")
                        s.writelines(str(self.value) + ", " + filename +"\n")
                        s.close()

        return

    def bollinger_trend_back(self, tickers, start):
        # lower than low line and rise back to bolling band --> buy
        # higher than upper band and drop down below bolling band --> sale
        # Loop tickers
        position = 0 # -2, -1, 1, 2
        preposition = 0 # -2, -1, 1, 2
        change = 0 # -1, 0, 1
        summaryfile = "D:\\backtest\\bollinger\\sum.txt"
        for ticker in tickers:
            # initial 10000, 10 transaction fee
            runquery = self.db.cursor()

            for day in range(10, 40, 2):
                # loop amplify of deviation 1.0 - 3.0
                for amplify in range(10, 30, 2):
                    amplify = amplify / 10
                    parameter = []
                    parameter.append(ticker)
                    parameter.append(day)
                    parameter.append(amplify)
                    parameter.append(start)
                    try:
                        args = runquery.callproc('p_bollinger', tuple(parameter))
                    except Error as e:
                        print(e)
                        return

                    for result in runquery.stored_results():
                        bollinger = result.fetchall()

                    # bollinger structure: code,dayid,date,days,amplify,Deviation,closeprice,ema,dema,upper,lower
                    # loop trend 0 - 2
                    for trend in range(0, 25, 2):
                        # adjust band
                        trend = trend / 10
                        print(ticker, day, amplify, trend)
                        self.cash = 10000
                        self.hold = 0
                        self.value = 10000
                        self.balance = []
                        for daybollinger in bollinger:
                            # check if total balance < 6666 stop test
                            # initial buy or not
                            if self.cash + self.hold * daybollinger[6] < 6666:
                                break

                            if daybollinger[6] > daybollinger[9] + trend * daybollinger[8]:
                                position = 2
                            elif daybollinger[6] > daybollinger[7] + trend * daybollinger[8]:
                                position = 1
                            elif daybollinger[6] > daybollinger[10] + trend * daybollinger[8]:
                                position = -1
                            else:
                                position = -2

                            if position != preposition:
                                change = position - preposition/abs(position - preposition)
                            else:
                                change = 0
                            preposition = position

                            if position == -1 and change == 1:
                                #buy
                                if self.hold == 0:
                                    unit = math.floor((self.cash - self.transaction) / daybollinger[6])
                                    self.hold = unit
                                    self.cash = self.cash - unit * daybollinger[6] - self.transaction

                            if position == 1 and change == -1:
                                #sale
                                if self.hold > 0:
                                    self.cash = self.cash + self.hold * daybollinger[6] - self.transaction
                                    self.hold = 0

                            self.value = self.cash + self.hold * daybollinger[6]
                            self.balance.append(
                                [ticker, daybollinger[2], daybollinger[6], self.cash, self.hold, self.value])

                        filename = "D:\\backtest\\bollinger\\" + ticker + '-ema' + str(day) + '-amplify' + str(amplify) + \
                                   '-trend' + str(trend) + '.txt'

                        f = open(filename, "w")
                        for bal in self.balance:
                            f.write(str(bal) + "\n")

                        f.close()

                        s = open(summaryfile, "a")
                        s.writelines(str(self.value) + ", " + filename + "\n")
                        s.close()

        return

    def KDJ(self):
        return

    def RSI(self):
        return

    def evaluate(self, parameter, balance):
        # return parameter, gain, deviation, period, benchmark,
        return
