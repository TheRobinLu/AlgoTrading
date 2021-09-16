
import MySql as sql

class Recommand:
    def __init__(self):
        self.mysql = sql.MySql()
        self.db = self.mysql.dbconn()

    def demark9Buy(self, tradeDay):

        runquery = self.db.cursor()
        query = "SELECT M.code FROM demarkpoint M, dayprice P WHERE M.code = P.code " \
                "AND M.dayId = P.dayId AND M.point < -6 AND date = '" + tradeDay +"'"
            tickers = self.mysql.get_tickers_id()

