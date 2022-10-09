import TradeData as td
import indicator as ind
from datetime import datetime as dt
from dateutil.relativedelta import *



# download data from yahoo daily data, 1min, 2min

myTd = td.TradeData()
#
myTd.get_new('')
# #
myTd.get_2min('', dt.now() + relativedelta(days=-5), dt.now())

myTd.get_min('', dt.now() + relativedelta(days=-4), dt.now())
#
# # # calculate indicator
MyInd = ind.Indicator()
MyInd.ema()
MyInd.kdj()
MyInd.rsi(tickers=[])
MyInd.demark9Point()

MyInd.KDJDaysInRange()

MyInd.RSIDaysInRange()

MyInd.Obv()


