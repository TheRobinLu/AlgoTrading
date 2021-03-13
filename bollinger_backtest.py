import strategy as st
import datetime as dt
import MySql as mysql
import backtest
#
# class bollinger_backtest(backtest):
#     def __init__(self):
#

def test_bollinger():
    myst = st.Strategy()
    mySQL = mysql.MySql()
    # tickers = mySQL.get_tickers_id()
    tickers = ['WPRT', 'WPRTT', 'WELL']
    # exclude = tickers
    # tickers = mySQL.get_tickers_id()
    # tickers = [ticker for ticker in tickers if ticker not in exclude]
    # tickers = [ticker for ticker in tickers if ticker > 'TCS']


    myst.bollinger_short_trend_back(tickers, dt.datetime.strptime("2019-01-01", "%Y-%m-%d"))


test_bollinger()
