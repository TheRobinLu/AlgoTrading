import MySql as sql
from mysql.connector import Error
import math
import os


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
            summaryfile = "D:\\backtest\\bollinger\\" + ticker + "sum.txt"
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
                            action = ""
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
                                    action = "UBBB" #"up back band buy"

                            if position == 1 and change == -1:
                                #sale
                                if self.hold > 0:
                                    self.cash = self.cash + self.hold * daybollinger[6] - self.transaction
                                    self.hold = 0
                                    action = "DTBS" # down to band sale

                            if position == 1 and change > -1 and self.hold == 0:
                                # check 3 day dema > 0
                                demaSQL = "SELECT dema FROM ema WHERE code = %s and dayid = %s and days = 3"
                                runquery.execute(demaSQL, tuple([ticker, daybollinger[1]]))
                                result = runquery.fetchone()
                                if result[0] > 0:
                                    unit = math.floor((self.cash - self.transaction) / daybollinger[6])
                                    self.hold = unit
                                    self.cash = self.cash - unit * daybollinger[6] - self.transaction
                                    action = 'IUTB' # in band up trend buy

                            self.value = self.cash + self.hold * daybollinger[6]
                            self.balance.append([ticker, daybollinger[2], daybollinger[6], self.cash, self.hold, self.value])

                        filename = "D:\\backtest\\bollinger\\" + ticker + '-ema' + str(day) + '-amplify' + str(amplify) + \
                                   '-trend' + str(trend) + '.txt'

                        f = open(filename, "w")
                        for bal in self.balance:
                            f.write(str(bal[0]) + "," + bal[1].strftime("%Y-%m-%d") + "," + '{:9.2f}'.format(bal[2]) + "," + \
                                    '{:9.2f}'.format(bal[3]) + "," + str(bal[4]) + "," + '{:9.2f}'.format(bal[5]) + action+"\n")
                        f.close()

                        s = open(summaryfile, "a")
                        s.writelines('{:9.2f}'.format(self.value) + "," + str(day) + "," + str(amplify) + "," + str(trend) + "\n")
                        s.close()

        return

    def bollinger_short_trend_back(self, tickers, start):
        # trend using short ema instead of main ema
        # lower than low line and rise back to bolling band --> buy
        # higher than upper band and drop down below bolling band --> sale
        # Loop tickers
        #
        position = 0 # -2, -1, 1, 2
        preposition = 0 # -2, -1, 1, 2
        change = 0 # -1, 0, 1


        # summaryfile = "D:\\backtest\\bollinger_back\\sum.txt"
        for ticker in tickers:
            path = "D:\\backtest\\bollinger_back\\"
            if not os.path.exists(path):
                os.mkdir(path)
            summaryfile = path + "sum_" +ticker + ".csv"
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
                        discard = False
                        trend = trend / 10
                        print(ticker, day, amplify, trend)
                        self.cash = 10000
                        self.hold = 0
                        self.value = 10000
                        self.balance = []
                        self.startprice = 0
                        self.status = 0 # -3...3
                        for daybollinger in bollinger:
                            # check if total balance < 6666 stop test
                            # initial buy or not
                            action = ""

                            if self.startprice == 0:
                                self.startprice = daybollinger[6]
                            if self.cash + self.hold * daybollinger[6] < daybollinger[6]/self.startprice * 7500:
                                discard = True
                                break
                            if daybollinger[6] > (daybollinger[9] + trend * daybollinger[8]) * 1.05:
                                position = 3
                            elif daybollinger[6] > daybollinger[9] + trend * daybollinger[8]:
                                position = 2
                            elif daybollinger[6] > daybollinger[7] + trend * daybollinger[8]:
                                position = 1
                            elif daybollinger[6] > daybollinger[10] + trend * daybollinger[8]:
                                position = -1
                            elif daybollinger[6] > (daybollinger[10] + trend * daybollinger[8]) * 0.95:
                                position = -2
                            else:
                                position = -3

                            if position != preposition:
                                change = (position - preposition)/abs(position - preposition)
                            else:
                                change = 0
                            preposition = position

                            if position == -3:
                                #buy
                                self.status = -3
                                if self.hold == 0:
                                    unit = math.floor((self.cash - self.transaction) / daybollinger[6])
                                    self.hold = unit
                                    self.cash = self.cash - unit * daybollinger[6] - self.transaction
                                    action = "DDB" #"deep down buy"

                            if position == -1 and change == 1:
                                #buy
                                self.status = -2
                                if self.hold == 0:
                                    unit = math.floor((self.cash - self.transaction) / daybollinger[6])
                                    self.hold = unit
                                    self.cash = self.cash - unit * daybollinger[6] - self.transaction
                                    action = "UBBB" #"up back band buy"

                            if position == 1 and change > -1:
                                # check 3 day dema > 0
                                demaSQL = "SELECT dema/ema FROM ema WHERE code = %s and dayid = %s and days = 3"
                                runquery.execute(demaSQL, tuple([ticker, daybollinger[1]]))
                                result = runquery.fetchone()
                                if result[0] > 0.002:
                                    self.status = -1
                                    if self.hold == 0:
                                        unit = math.floor((self.cash - self.transaction) / daybollinger[6])
                                        self.hold = unit
                                        self.cash = self.cash - unit * daybollinger[6] - self.transaction
                                        action = 'IHUB'  # in high band up trend buy

                            if position == -1 and change < 1:
                                # check 3 day dema < 0
                                demaSQL = "SELECT dema/ema FROM ema WHERE code = %s and dayid = %s and days = 3"
                                runquery.execute(demaSQL, tuple([ticker, daybollinger[1]]))
                                result = runquery.fetchone()
                                if result[0] < -0.002:
                                    self.status = 1
                                    if self.hold > 0:
                                        self.cash = self.cash + self.hold * daybollinger[6] - self.transaction
                                        self.hold = 0
                                        action = "ILDS" #in low band, down trend sale

                            if position == 1 and change == -1:
                                #sale
                                self.status = 2
                                if self.hold > 0:
                                    self.cash = self.cash + self.hold * daybollinger[6] - self.transaction
                                    self.hold = 0
                                    action = "DTBS" # down to band sale

                            if position == 3:
                                #buy
                                self.status = 3
                                if self.hold > 0:
                                    self.cash = self.cash + self.hold * daybollinger[6] - self.transaction
                                    self.hold = 0
                                    action = "SHS" #"Super High Sale"

                            self.value = self.cash + self.hold * daybollinger[6]
                            self.balance.append([ticker, daybollinger[2], daybollinger[6], self.cash, self.hold,
                                                 self.value, action, self.status, daybollinger[6]/self.startprice * 10000])
                        if not discard:
                            filename = path + ticker + '-ema' + str(day) + '-amplify' + str(amplify) + \
                                       '-trend' + str(trend) + '.csv'

                            f = open(filename, "w")
                            for bal in self.balance:
                                f.write(str(bal[0]) + "," + bal[1].strftime("%Y-%m-%d") + "," + '{:9.2f}'.format(bal[2]) +
                                        "," + '{:9.2f}'.format(bal[3]) + "," + str(bal[4]) + "," +
                                        '{:9.2f}'.format(bal[5]) + "," + bal[6] + "," + str(bal[7]) + "," +
                                        '{:9.2f}'.format(bal[8]) + "\n")
                            f.close()

                            if len(self.balance) > 1:
                                s = open(summaryfile, "a")
                                s.writelines('{:9.2f}'.format(self.value) + "," + str(day) + "," + str(amplify) + "," +
                                             str(trend) + "," + '{:9.2f}'.format(self.balance[-1][8]) + "\n")
                                s.close()
        return

    def bollinger_short_trend_DB(self, tickers, start):
        # trend using short ema instead of main ema
        # lower than low line and rise back to bolling band --> buy
        # higher than upper band and drop down below bolling band --> sale
        # Loop tickers
        #
        position = 0 # -2, -1, 1, 2
        preposition = 0 # -2, -1, 1, 2
        change = 0 # -1, 0, 1


        # summaryfile = "D:\\backtest\\bollinger_back\\sum.txt"
        for ticker in tickers:
            path = "D:\\backtest\\bollinger_back\\"
            if not os.path.exists(path):
                os.mkdir(path)
            summaryfile = path + "sum_" +ticker + ".csv"
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
                        discard = False
                        trend = trend / 10
                        print(ticker, day, amplify, trend)
                        self.cash = 10000
                        self.hold = 0
                        self.value = 10000
                        self.balance = []
                        self.startprice = 0
                        self.status = 0 # -3...3
                        for daybollinger in bollinger:
                            # check if total balance < 6666 stop test
                            # initial buy or not
                            action = ""

                            if self.startprice == 0:
                                self.startprice = daybollinger[6]
                            if self.cash + self.hold * daybollinger[6] < daybollinger[6]/self.startprice * 8500:
                                discard = True
                                break
                            if daybollinger[6] > (daybollinger[9] + trend * daybollinger[8]) * 1.10:
                                position = 3
                            elif daybollinger[6] > daybollinger[9] + trend * daybollinger[8]:
                                position = 2
                            elif daybollinger[6] > daybollinger[7] + trend * daybollinger[8]:
                                position = 1
                            elif daybollinger[6] > daybollinger[10] + trend * daybollinger[8]:
                                position = -1
                            elif daybollinger[6] > (daybollinger[10] + trend * daybollinger[8]) * 0.90:
                                position = -2
                            else:
                                position = -3

                            if position != preposition:
                                change = (position - preposition)/abs(position - preposition)
                            else:
                                change = 0
                            preposition = position

                            if position == -3:
                                #buy: below 10% low band
                                self.status = -3
                                if self.hold == 0:
                                    unit = math.floor((self.cash - self.transaction) / daybollinger[6])
                                    self.hold = unit
                                    self.cash = self.cash - unit * daybollinger[6] - self.transaction
                                    action = "DDB" #"deep down buy"

                            if position == -1 and change == 1:
                                #buy
                                self.status = -2
                                if self.hold == 0:
                                    unit = math.floor((self.cash - self.transaction) / daybollinger[6])
                                    self.hold = unit
                                    self.cash = self.cash - unit * daybollinger[6] - self.transaction
                                    action = "UBBB" #"up back band buy"

                            if position == 1 and change > -1:
                                # check 3 day dema > 0
                                demaSQL = "SELECT dema/ema FROM ema WHERE code = %s and dayid = %s and days = 3"
                                runquery.execute(demaSQL, tuple([ticker, daybollinger[1]]))
                                result = runquery.fetchone()
                                if result[0] > 0.002:
                                    self.status = -1
                                    if self.hold == 0:
                                        unit = math.floor((self.cash - self.transaction) / daybollinger[6])
                                        self.hold = unit
                                        self.cash = self.cash - unit * daybollinger[6] - self.transaction
                                        action = 'IHUB'  # in high band up trend buy

                            if position == -1 and change < 1:
                                # check 3 day dema < 0
                                demaSQL = "SELECT dema/ema FROM ema WHERE code = %s and dayid = %s and days = 3"
                                runquery.execute(demaSQL, tuple([ticker, daybollinger[1]]))
                                result = runquery.fetchone()
                                if result[0] < -0.002:
                                    self.status = 1
                                    if self.hold > 0:
                                        self.cash = self.cash + self.hold * daybollinger[6] - self.transaction
                                        self.hold = 0
                                        action = "ILDS" #in low band, down trend sale

                            if position == 1 and change == -1:
                                #sale
                                self.status = 2
                                if self.hold > 0:
                                    self.cash = self.cash + self.hold * daybollinger[6] - self.transaction
                                    self.hold = 0
                                    action = "DTBS" # down to band sale

                            if position == 3:
                                #buy
                                self.status = 3
                                if self.hold > 0:
                                    self.cash = self.cash + self.hold * daybollinger[6] - self.transaction
                                    self.hold = 0
                                    action = "SHS" #"Super High Sale"

                            self.value = self.cash + self.hold * daybollinger[6]
                            self.balance.append([ticker, daybollinger[2], daybollinger[6], self.cash, self.hold,
                                                 self.value, action, self.status, daybollinger[6]/self.startprice * 10000])
                        if not discard:
                            filename = path + ticker + '-ema' + str(day) + '-amplify' + str(amplify) + \
                                       '-trend' + str(trend) + '.csv'

                            f = open(filename, "w")
                            for bal in self.balance:
                                f.write(str(bal[0]) + "," + bal[1].strftime("%Y-%m-%d") + "," + '{:9.2f}'.format(bal[2]) +
                                        "," + '{:9.2f}'.format(bal[3]) + "," + str(bal[4]) + "," +
                                        '{:9.2f}'.format(bal[5]) + "," + bal[6] + "," + str(bal[7]) + "," +
                                        '{:9.2f}'.format(bal[8]) + "\n")
                            f.close()

                            if len(self.balance) > 1:
                                s = open(summaryfile, "a")
                                s.writelines('{:9.2f}'.format(self.value) + "," + str(day) + "," + str(amplify) + "," +
                                             str(trend) + "," + '{:9.2f}'.format(self.balance[-1][8]) + "\n")
                                s.close()
        return

    def KDJ(self):
        return

    def RSI(self):
        return

    def evaluate(self, parameter, balance):
        # return parameter, gain, deviation, period, benchmark,
        return
