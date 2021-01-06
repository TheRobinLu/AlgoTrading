import strategy as st
import datetime as dt




def test_bollinger():
    myst = st.Strategy()
    tickers = ["ARKK", "FB"]
    myst.bollinger_trend_back(tickers, dt.datetime.strptime("2017-01-01", "%Y-%m-%d"))


test_bollinger()
