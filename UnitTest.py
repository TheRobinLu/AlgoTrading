import yfinance as yf
from datetime import datetime as dt


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
    a = '2020-12-14 00:00:00'

def replace():
    a = 'Peter is a {0} dog, but {1}'
    l = ['nice', 'he can not swim.']
    t = tuple(l)
    print(a.format(t))

#def download_new():


#downloadmin()
#checkListEmpty()
replace()




