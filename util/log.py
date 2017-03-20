from logging.handlers import RotatingFileHandler
import logging

class log:
    logger = logging.getLogger('searchLog')
    searchLog = RotatingFileHandler("./log/history.log", maxBytes=50000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s USER[%(user)s] SEARCH[%(question)s] ANSWER[%(answer)s] RESULT[%(questions)s]')
    searchLog.setFormatter(formatter)
    logger.addHandler(searchLog)
    logger.setLevel(logging.INFO)

    @classmethod
    def writeLog(cls,user,question, answerID, questionIDs):
        questions = ""
        for i in range(0, len(questionIDs)):
            if i == 0:
                questions = questionIDs[0]
            else:
                questions =  questions + "|" + questionIDs[i]
        data={"user":user,"question":question,"answer":answerID ,"questions":questions}
        cls.logger.info("",extra=data)
