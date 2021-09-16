import Scanner
import datetime as dt


class KDJScanner(Scanner.Scanner):

    def scan(self):
        super().Scan()
        self.strategy = 'KDJ'

        self.Parameter()
        print('starting', self.strategy)
        for ticker in self.tickers:
            for pid in self.params:
                runQuery = self.db.cursor()
                now = self.date

                # query = "call p_RSIEvaluate_center ( '" + ticker + "', " + str(pid[0]) + ", '2021-03-16-20:00:00')"
                # runQuery.execute(query)
                runQuery.callproc("p_KDJEvaluate", tuple([ticker, pid, now]))
                self.db.commit()
                print(self.strategy, ticker, pid)



# test = KDJScanner()
# test.scan()
