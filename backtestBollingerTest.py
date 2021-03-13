import backtestBollinger
import MySql as sql
from mysql.connector import Error
import datetime as dt


def callProc():
    aa = sql.MySql()
    db = aa.dbconn()
    start = dt.datetime.strptime("2008-01-01", "%Y-%m-%d")
    end = dt.datetime.strptime("2010-01-01", "%Y-%m-%d")
    runquery = db.cursor()
    pp = []
    pp.append('MEOH')
    pp.append(10)
    pp.append(5)
    pp.append(3)
    pp.append(start)
    pp.append(end)

    print(tuple(pp))
    try:
        runquery.callproc("p_bollinger_trend", tuple(['ARKK',10,5,3,start,end]))
    except Error as e:
        print(e)
    for result in runquery.stored_results():
        data = result.fetchall()
    print(data)

    return


def singleTest():
    myTest = backtestBollinger.BackTestBollinger()
    myTest.TrainStart = dt.datetime.strptime("2012-01-01", "%Y-%m-%d")
    myTest.TrainEnd = dt.datetime.strptime("2022-01-01", "%Y-%m-%d")
    myTest.strategyName = "bollinger"
    myTest.ticker = 'ARKK'
    myTest.getStrategy(myTest.getStrategyId())

    myTest.Training()
    print(myTest.strategyId)


#callProc()

singleTest()
