import DeMark9Scanner
import KDJScanner
import RSIScanner
import KDJ_DIRScanner
import RSI_DIRScanner
import datetime as dt


def scan():
    print(dt.datetime.now(), "start")
    scanner = DeMark9Scanner.DeMark9Scanner()
    scanner.scan()
    scanner = RSIScanner.RSIScanner()
    scanner.scan()
    scanner = KDJScanner.KDJScanner()
    scanner.scan()
    scanner = RSI_DIRScanner.RSI_DIRScanner()
    scanner.scan()
    scanner = KDJ_DIRScanner.KDJ_DIRScanner()
    scanner.scan()
    print(dt.datetime.now(), "end")


def scanByDate(date):

    scanner = DeMark9Scanner.DeMark9Scanner()
    scanner.date = date
    scanner.scan()
    scanner = RSIScanner.RSIScanner()
    scanner.date = date
    scanner.scan()
    scanner = KDJScanner.KDJScanner()
    scanner.date = date
    scanner.scan()

scan()

# scanByDate(dt.date(2021, 1, 29))
#
# scanByDate(dt.date(2021, 2, 16))
#
# scanByDate(dt.date(2021, 3, 1))


