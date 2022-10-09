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
        query = "SELECT code FROM equity "
        #runquery.execute(query, tuple([(dt.today() + relativedelta(months=-2)).strftime("%Y-%m-%d %H:%M:%S")]))
        runquery.execute(query)

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

    def analysis_rsi_performance(self):
        #populate strategy_day for RSITrend Strategy p_analysis_rsi_perform_by_strategy
        # then strategy_equity_perform and strategy_equity_perform_possibility
        # p_analysis_rsi_perform_by_strategy -- p_analysis_summarize_possiblity
        strategyIds = []
        runquery = self.db.cursor()
        #get strategies
        query = "SELECT id FROM strategy WHERE strategyGroup = 'RSITrend'"
        runquery.execute(query)

        result = runquery.fetchall()

        #strategyIds = int(''.join(map(str, result)))
        #strategyIds = list(result)
        for a in result:
         #   strategyIds.append(int(a))
            strategyIds.append(a[0])
        print(strategyIds)
        for ticker in self.tickers:
            for strategy in strategyIds:

                runquery.callproc("p_analysis_rsi_perform_by_strategy", tuple([ticker, str(strategy)]))
                self.db.commit()
                print(dt.now(), "Completed p_analysis_rsi_perform_by_strategy", ticker, strategy )

    def days_after_perform(self):
        #populate data to equity_daysafter_perform via p_daysafter_perform_day
        runquery = self.db.cursor()
        days = [1,2,3,5,8,13]
        for ticker in self.tickers:
            for day in days:
                # populate data to equity_daysafter_perform

                runquery.callproc("p_daysafter_perform_day", tuple([ticker, day]))
                self.db.commit()
                print(dt.now(), "Completed p_daysafter_perform_day for ", ticker, day)


    def analysis_demark_performance(self):
        #populate strategy_day for Demark Strategy by p_analysis_demark_perform_by_strategy,
        # then strategy_equity_perform and strategy_equity_perform_possibility
        # p_analysis_rsi_perform_by_strategy -- p_analysis_summarize_possiblity
        runquery = self.db.cursor()

        for ticker in self.tickers:
            for point in range(-15, 16):

                runquery.callproc("p_analysis_demark_perform_by_point", tuple([ticker, str(point)]))
                self.db.commit()
                print(dt.now(), "Completed p_analysis_demark_perform_by_point", ticker, point )

    def run(self):
        self.get_tickers()
        #self.analysis_tickers_performance() #abandent function
        #self.analysis_performance() #abandent function
        #self.days_after_perform()
        #self.analysis_rsi_performance()
        self.analysis_demark_performance()
p = Performance()
p.run()






