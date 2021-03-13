from datetime import datetime as dt
import datetime 


class Log:
    logfile = "YTD.log"
    showMessage = True
    logMessage = True

    def showMessage(self, on):
        self.showMessage = on

    def logMessage(self, on):
        self.logMessage = on

    def error(self, message):
        self.log(message, "Error")

    def warning(self, message):
        self.log(message, "Warning")

    def infor(self, message):
        self.log(message, "Infor")

    def log(self, message, log_type):
        f = open(self.logfile, "a")
        now = dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        log_text = now + " " + log_type + " " + message
        f.write(log_text + "\n") 
        if self.showMessage:
            print(log_text)
        f.close()
