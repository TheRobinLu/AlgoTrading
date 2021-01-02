### import yfinance as yf
import MySql as sql
import pandas as pd
import numpy as np

DB = sql.MySql.dbconn(sql.MySql)

#regionDDL
#region CreateEquity
query = DB.cursor()
sql = "SELECT 1 FROM information_schema.tables where table_name ='equity'"
query.execute(sql)
result = query.fetchone()
if result[0] != 1:
    sql = "CREATE TABLE `equity` ("\
          "`code` varchar(20) NOT NULL,"\
          "`equityName` varchar(120) DEFAULT NULL,"\
          "`type` varchar(10) DEFAULT NULL,"\
          "`currency` varchar(3) DEFAULT NULL,"\
          "`yahooCode` varchar(20) DEFAULT NULL,"\
          "`inverstingCode` varchar(20) DEFAULT NULL,"\
          "`iTradeCode` varchar(20) DEFAULT NULL,"\
          "`IBCode` varchar(20) DEFAULT NULL,"\
          "PRIMARY KEY (`code`)"\
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"
    query.execute(sql)

#endregion
#endregion


#region Script ##

#endregion


#region DML ##
dml = DB.cursor()

## Data loading
##@ Load Equity
equity = pd.read_csv("Equity.csv")
equity.head()
if len(equity) > 0:
    sql = "DELETE FROM Equity"
    dml.execute(sql)
    DB.commit()

equity = equity.replace(np.nan, '')
for i, row in equity.iterrows():
    sql = "INSERT INTO Equity (code, equityName, type, currency, yahooCode, inverstingCode, iTradeCode, IBCode)" \
           " VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
    dml.execute(sql, tuple(row))
    DB.commit()

### Load ....

#endregion