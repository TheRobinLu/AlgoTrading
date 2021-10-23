import MySql as sql
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta


class Performance:
    tickers = []

    def __init__(self):
        self.mysql = sql.MySql()
        self.db = self.mysql.dbconn()

    def get_tickers(self):
        #get
        runquery = self.db.cursor()
        query = "SELECT code FROM equity WHERE code not in " \
                "(SELECT Distinct code FROM equity_strategy_performance " \
                "WHERE UpdateDT > %s) LIMIT 110"
        runquery.execute(query, tuple([(dt.today() + relativedelta(months=-2)).strftime("%Y-%m-%d %H:%M:%S")]))

        result = runquery.fetchall()
        for a in result:
            self.tickers.append(''.join(a))

        return

    def analysis_tickers_performance(self):
        runquery = self.db.cursor()
        for ticker in self.tickers:

            runquery.callproc("p_equity_strategy_performance_Demark", tuple([ticker]))
            self.db.commit()
            print(dt.now(), "Completed p_equity_strategy_performance_Demark for ", ticker)

            runquery.callproc("p_equity_strategy_performance_KDJobt", tuple([ticker]))
            self.db.commit()
            print(dt.now(), "Completed p_equity_strategy_performance_KDJobt for ", ticker)

            runquery.callproc("p_equity_strategy_performance_RSI", tuple([ticker]))
            self.db.commit()
            print(dt.now(), "Completed p_equity_strategy_performance_RSI for ", ticker)

    def analysis_performance(self):
        runquery = self.db.cursor()
        runquery.callproc("p_strategy_performance")
        self.db.commit()
        print(dt.now(), "Completed p_strategy_performance")

    def run(self):
        self.get_tickers()
        self.analysis_tickers_performance()
        #self.analysis_performance()


p = Performance()
p.run()






