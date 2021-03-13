import MySql as sql
import bollingerStrategy as boll
from mysql.connector import Error
import backtestEntity as bte


myBoll = boll.BollingerStrategy()
myBoll.generateParameter()
# bollingers = myBoll.getParameter()
