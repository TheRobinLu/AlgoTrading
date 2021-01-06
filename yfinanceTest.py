import yfinance as yf
import MySql as sql
import pandas as pd
import numpy as np
from datetime import datetime as dt
from dateutil.relativedelta import *

def max_download_period():
    data = yf.download('Z', interval="2m", start="2021-01-01", group_by="ticker")
    print (data)


max_download_period()