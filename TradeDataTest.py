import TradeData as td
from datetime import datetime as dt
from dateutil.relativedelta import *

def retrieve_tickers():
    myTd = td.TradeData()
    data = myTd.get_tickers()
    tickers = []
    for a in data:
        tickers.append(''.join(a))
        # if tickers == '':
        #     tickers = tickers.join(a)
        # else:
        #     tickers = tickers + '\t' + tickers.join(a)
    print(tickers)


def download_all():
    myTd = td.TradeData()
    tickers = []
    myTd.get_all(tickers)

def createIndicator():
    myTd = td.TradeData()

    myTd.calculateIndicators('ARKK')

def get_new():
    myTd = td.TradeData()

    myTd.get_new('')

def get_new():
    myTd = td.TradeData()
    myTd.get_new('')

def get_min():
    myTd = td.TradeData()
    myTd.get_min('', dt.now() + relativedelta(days=-7), dt.now())

def get_realtime():
    myTd = td.TradeData()
    tickers = ['ARKK', 'ARKW', 'HUYA', 'TSLA']
    myTd.get_realtime(tickers, dt.now() + relativedelta(minutes=-10))

def monitor():
    myTd = td.TradeData()
    tickers = ['ARKK', 'ARKW', 'HUYA', 'TSLA']
    myTd.monitor(tickers)


#download_all()
#createIndicator()
#get_new()
get_min()
#get_realtime()

#monitor()