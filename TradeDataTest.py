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

    myTd.calculateIndicators('')


def get_new():
    myTd = td.TradeData()
    tickers = ['EMA.TO', 'EAAI.NE']
    myTd.get_new(tickers)

def get_hour():
    myTd = td.TradeData()
    tickers = ['EAAI.NE']
    myTd.get_hour(tickers)

def get_min():
    myTd = td.TradeData()
    myTd.get_min(['WCP.TO', 'WELL.TO', 'WPRT', 'WPRT.TO','XQQ.TO','XSP.TO'], dt.now() + relativedelta(days=-2), dt.now())

def get_2min():
    myTd = td.TradeData()
    myTd.get_2min(['WCP.TO', 'WELL.TO', 'WPRT', 'WPRT.TO','XQQ.TO','XSP.TO'], dt.now() + relativedelta(days=-2), dt.now())

def get_realtime():
    myTd = td.TradeData()
    tickers = ['ARKK', 'ARKW', 'HUYA', 'TSLA']
    myTd.get_realtime(tickers, dt.now() + relativedelta(minutes=-10))

def monitor():
    myTd = td.TradeData()
    tickers = ['EMA', 'TSLA']
    myTd.monitor(tickers)


#download_all()
#createIndicator()
#get_new()
get_hour()
# get_min()
# get_2min()
#get_realtime()

#monitor()