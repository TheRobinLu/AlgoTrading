import MySql as sql
from mysql.connector import Error
import backtestEntity as bte


class BollingerStrategy:
    emaDays = []
    amplify = []
    demaDays = []
    demaAmplify = []
    shortTrend = []

    def __init__(self):
        aa = sql.MySql()
        self.db = aa.dbconn()

    def generateParameter(self):
        runquery = self.db.cursor()
        query = "SELECT id FROM strategy WHERE strategyName = 'bollinger' "
        runquery.execute(query)
        result = runquery.fetchone()
        id = int(result[0])
        k = 0
        query = "INSERT INTO strategyparameters (strategyid, intP1, intP2, intP3, decP5, decP6)" \
                " VALUES (%s, %s, %s, %s, %s, %s)"

        for i in range(10, 42, 2):
            self.emaDays.append(i)
        print("self.emaDays.append(")
        for i in range(3, 9):
            self.demaDays.append(i)
        print("self.demaDays.append(i")
        for i in range(3, 6):
            self.shortTrend.append(i)
        print("self.shortTrend.append(i")

        for i in range(10, 40, 2):
            self.amplify.append(i/10)
        print("self.amplify.append(i")

        for i in range(0, 30, 2):
            self.demaAmplify.append(i/10)
        print("self.demaAmplify.append(i")

        for emaDay in self.emaDays:
            for demaDay in self.demaDays:
                for short in self.shortTrend:
                    if short >= demaDay:
                        continue
                    for amp in self.amplify:
                        for demaAmp in self.demaAmplify:
                            exist = "SELECT count(*) FROM strategyparameters " \
                                    "WHERE strategyid = %s AND intP1 = %s AND intP2 = %s AND intP3 = %s " \
                                    "AND decP5 = %s AND decP6 = %s"
                            runquery.execute(exist, tuple([id, emaDay, demaDay, short, amp, demaAmp]))
                            result = runquery.fetchone()
                            isSaved = int(result[0])
                            if isSaved == 0:
                                runquery.execute(query, tuple([id, emaDay, demaDay, short, amp, demaAmp]))
                                self.db.commit()
                                print(k)
                                k = k + 1
        print("Parameters Generated!")

    def getParameter(self):
        bollingers = []
        runquery = self.db.cursor()
        query = "SELECT SP.* FROM strategyparameters SP INNER JOIN strategy S ON SP.strategyID = S.id " \
                "WHERE strategyName = 'bollinger'"
        runquery.execute(query)
        result = runquery.fetchall()
        for x in result[0]:
            newBollinger = Bollinger()
            newBollinger.parameterId = x[0]
            newBollinger.strategyId = x[1]
            newBollinger.emaDay = x[2]
            newBollinger.demaDay = x[3]
            newBollinger.short = x[4]
            newBollinger.amp = x[5]
            newBollinger.demaAmp = x[6]

            bollingers.append(newBollinger)

        return bollingers


class Bollinger:
    parameterId = 0
    strategyId = 0
    emaDay = 0
    amp = 0
    demaDay = 0
    demaAmp = 0
    short = 0




