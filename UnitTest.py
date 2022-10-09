import yfinance as yf
from datetime import datetime as dt
import datetime
import pytz
import time
from dateutil import tz
from collections import namedtuple
import TradeData


def downloadmin():
    msft = yf.Ticker("000001.SS")
    #print(msft.financials)
    #print(msft.major_holders)
    tickers = ["MSFT", "ARKK"]
    data = yf.download("MSFT ARKK", interval="1m", start=dt.fromisoformat('2020-12-21'), group_by='ticker')
    #data = yf.download("MSFT",  group_by='ticker')

#    print(data.values)

    tradingMin = data.index
    for ticker in tickers:
        for t in tradingMin:
            print(ticker, t, data[ticker].Open[t], data[ticker].High[t], data[ticker].Low[t], data[ticker].Close[t],\
                  data[ticker].Volume[t])
        #    print(t, data.ARKK.Open[t], data.High[t], data.Low[t], data.Close[t], data.Volume[t] )
        # for i in range(data.Close):
        #     print(tradingMin[i])


def checkListEmpty():
    a = []
    if len(a) != 0:
        print(a)
    else:
        print('I am null')

def strToDate():
    a = dt.now().strftime("%Y-%m-%d")
    print(a)

def DateTimetoDate():
    a = dt.now()
    b = a.replace(hour=0, minute=0, second=0, microsecond=0) # Returns a copy
    c = b + datetime.timedelta(minutes=15)
    print(b, type(b))
    print(c, type(c))

def timeZone():
    d = dt.now()
    print(d)
    # timezone = pytz.timezone(-5)
    a = d.astimezone(tz = tz.tzlocal())
    print(a)

    print(tz.tzlocal())


def replace():
    a = 'Peter is a {0} dog, but {1}'
    l = ['nice', 'he can not swim.']
    t = tuple(l)
    print(a.format(t))


def nameTuple():
    a = ['','','']
    # a.append("ARKW")
    # a.append(dt.fromisoformat('2020-12-21'))
    #a.append(26.76)
    b = namedtuple("DayTrade", "Ticker Date Price")
    c = b(233,33,44)
    # b = namedtuple("DayTrade", ["Ticker", "Date", "Price"])
    # c = b("ARKW", dt.fromisoformat('2020-12-21'), 26.76)

    print(c)
    print(*a)
    print(b)

def obv():

#def download_hour():

#def download_new():


#downloadmin()
#checkListEmpty()
#replace()
#strToDate()
#DateTimetoDate()
#timeZone()
#nameTuple()



