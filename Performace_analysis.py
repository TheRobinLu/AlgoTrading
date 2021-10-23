#############################################################
# call p_bp_perform_ticker/ p_sp_perform_ticker
import MySql as sql
from datetime import datetime as dt


class Performance:
    def __init__(self):
        self.mysql = sql.MySql()
        self.db = self.mysql.dbconn()

    def RSI_perform(self):
        runquery = self.db.cursor()
        tickers = self.mysql.get_tickers_id()
        for ticker in tickers:
            runquery.callproc("p_rsi_perform_ticker", [ticker])


