from logging.handlers import RotatingFileHandler
import logging
import elasticsearch
import datetime
#
# es = elasticsearch.Elasticsearch(hosts=['172.31.8.129'])
# try:
#     es.indices.create('qa_log',body=
#     {
#         "mappings": {
#             "log": {
#                 "properties": {
#                     "time": {
#                         "type": "date"
#                     },
#                     "user": {
#                         "type": "string",
#                         "index": "not_analyzed"
#                     },
#                     "question": {
#                         "type": "string",
#                         "analyzer": "ik_smart"
#                     },
#                     "answer": {
#                         "type": "boolean"
#                     },
#                     "other_answer":{
#                         "type":"boolean"
#                     }
#                 }
#             }
#         }
#     }
#                       )
# except:
#     pass


class log:
    logger = logging.getLogger('searchLog')
    searchLog = RotatingFileHandler("./log/history.log", maxBytes=500000, backupCount=50)
    formatter = logging.Formatter(
        '%(asctime)s USER[%(user)s] SEARCH[%(question)s] ANSWER[%(answer)s] SCORE[%(score)s] RESULT[%(questions)s]')
    searchLog.setFormatter(formatter)
    logger.addHandler(searchLog)
    logger.setLevel(logging.INFO)


    @classmethod
    def writeLog(cls, user, question, answerID, maxScore, questionIDs):
        questions = ""
        question = question.replace("\n", "")
        for i in range(0, len(questionIDs)):
            if i == 0:
                questions = questionIDs[0]
            else:
                questions = questions + "|" + questionIDs[i]
        data = {"user": user, "question": question, "answer": answerID, "score": maxScore, "questions": questions}
        cls.logger.info("", extra=data)
        # try:
        #     es.index('qa_log','log',{'time':datetime.datetime.utcnow(),'user':user,
        #                              'question':question,'answer': len(answerID) == 0,'other_answer':len(questionIDs) == 0 })
        # except:
        #     pass