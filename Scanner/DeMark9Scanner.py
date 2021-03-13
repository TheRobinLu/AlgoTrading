import Scanner
import datetime as dt

class DeMark9Scanner(Scanner.Scanner):

    def scan(self):
        super().Scan()
        self.TickerList()

        for ticker in self.tickers:

            demark9SQL = 'SELECT code, Max(date), f_deMark9(code, now(), 14) FROM dayprice WHERE code = %s AND ' + \
                            'date <= now()'

            runQuery = self.db.cursor()

            runQuery.execute(demark9SQL, tuple([ticker]))
            data = runQuery.fetchall()
            a = self._Result(*data[0])
            self.results.append(a)

        for a in self.results:
            print(a.code, dt.datetime.strftime(a.date, "%Y-%m-%d"), a.demark)


test = DeMark9Scanner()
test.scan()
