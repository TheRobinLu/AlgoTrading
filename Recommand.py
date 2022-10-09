
import MySql as sql
from datetime import datetime as dt

class Recommand:
    def __init__(self):
        self.mysql = sql.MySql()
        self.db = self.mysql.dbconn()

    def demark9Buy(self, tradeDay):

        runquery = self.db.cursor()
        query = "SELECT M.code FROM demarkpoint M, dayprice P WHERE M.code = P.code " \
                "AND M.dayId = P.dayId AND M.point < -6 AND date = '" + tradeDay +"'"
        tickers = self.mysql.get_tickers_id()

    def deviate(self, tradeDay):
        tickers = self.mysql.get_tickers_id()
        runquery = self.db.cursor()

        for ticker in tickers:
            days = [7, 14, 21]
            ranges = [2, 3, 4, 5]

            #do RSI
            for day in days:
                for range in ranges:
                    runquery.callproc("p_deviate", tuple([ticker, tradeDay, 'RSI', day, range]))
                    self.db.commit()
                    for result in runquery.stored_results():
                        print(result.fetchall())


            #do KDJ


            days = [6, 9, 18]
            for day in days:
                for range in ranges:
                    runquery.callproc("p_deviate", tuple([ticker, tradeDay, 'KDJ', day, range]))
                    self.db.commit()
                    for result in runquery.stored_results():
                        print(result.fetchall())


day = dt.today()
myRecommand = Recommand()
myRecommand.deviate(day)