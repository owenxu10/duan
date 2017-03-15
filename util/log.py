from logging.handlers import RotatingFileHandler
import logging

class log:
    logger = logging.getLogger('searchLog')
    searchLog = RotatingFileHandler("./log/history.log", maxBytes=50000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s USER[%(user)s] SEARCH[%(question)s] RESULT[%(result)s]')
    searchLog.setFormatter(formatter)
    logger.addHandler(searchLog)
    logger.setLevel(logging.INFO)

    @classmethod
    def writeLog(cls,user,question,result):
        data={"user":user,"question":question,"result":result}
        cls.logger.info("",extra=data)
