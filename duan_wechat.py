# -*- coding: utf-8 -*-
import datetime
import falcon
import json
import os
import time
from elasticsearch import Elasticsearch
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage, EventMessage

from util.cache import redisServer
from config import wechatConfig, replyConfig
from util.util import handleQuestion, afterSearch, findGreeting, getReply
from util.log import log


class duanWechat(object):
    def __init__(self):
        self.wechat = WechatBasic(conf=wechatConfig)
        self.es = Elasticsearch()

    def on_get(self, req, resp):
        signature = req.params['signature']
        echostr = req.params['echostr']
        timestamp = req.params['timestamp']
        nonce = req.params['nonce']
        # """Handles GET requests"""
        if self.wechat.check_signature(signature, timestamp, nonce):
            resp.status = falcon.HTTP_200  # This is the default status
            resp.body = echostr

    def on_post(self, req, resp):
        reply = ''
        result = False
        today = datetime.date.today()
        xml_str = str(req.stream.read().decode("utf-8"))

        try:
            self.wechat.parse_data(xml_str)
            user = self.wechat.message.source
            createdTime = self.wechat.message.time
            if isinstance(self.wechat.message, TextMessage):
                saidHello = self.sayHello(user, today, createdTime)
                content = self.wechat.message.content
                try:
                    # content is number
                    number = int(content) - 1
                    if number >= 0 and number < redisServer.getQuestionLength(user) and redisServer.getQuestionLength(
                            user) > 0:

                        if len(redisServer.getHref(user, number).decode("utf-8")) != 0:
                            reply = getReply(
                                     redisServer.getQuestion(user, number).decode("utf-8"),
                                     redisServer.getAnswer(user, number).decode("utf-8"),
                                     redisServer.getHref(user, number).decode("utf-8"),
                                     redisServer.getTitle(user, number).decode("utf-8")
                                     )
                        else:
                            reply = getReply(redisServer.getQuestion(user, number).decode("utf-8"),
                                     redisServer.getAnswer(user, number).decode("utf-8"))
                    else:
                        reply = replyConfig['not_found']

                except ValueError:
                    # content is text
                    if findGreeting(content) and not saidHello:
                        self.wechat.send_text_message(user,self.setWelcomeWord(createdTime))
                        reply = replyConfig["greeting"]

                    else:
                        reply, result = self.searchQuestion(user, content)
                        # log_server
                        log.writeLog(user, content, result)

                resp.status = falcon.HTTP_200
                resp.body = self.wechat.response_text(content=reply)

            elif isinstance(self.wechat.message, EventMessage):
                if self.wechat.message.type == 'subscribe':
                    if not redisServer.ifUserLogged(today, user):
                        redisServer.setUser(today, user)
                    resp.status = falcon.HTTP_200
                    reply = replyConfig['welcome']
                    resp.body = self.wechat.response_text(content=reply)
            else:
                resp.status = falcon.HTTP_200
                reply = replyConfig['not_found']
                resp.body = self.wechat.response_text(content=reply)
        except ParseError:

            resp.status = falcon.HTTP_200
            resp.body = ""

    def searchQuestion(self, user, question):
        result = True
        # handleQuestion
        (question_sequence, question, period) = handleQuestion(question)

        query_data = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": question_sequence,
                                "fields": [
                                    "question^2",
                                    "answer^1"
                                ],
                                "boost": 1
                            }
                        },
                        {
                            "match_phrase": {
                                "question": {
                                    "query": question_sequence,
                                    "boost": 3
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "answer": {
                                    "query": question_sequence,
                                    "slop": 0,
                                    "boost": 2
                                }
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "pre_tags": [
                    ""
                ],
                "post_tags": [
                    ""
                ],
                "fields": {
                    "question": {},
                    "answer": {}
                }
            }
        }
        res = self.es.search(index="qa_demo", body=json.dumps(query_data, ensure_ascii=False))

        filtered_hits, maxScore, took = afterSearch(res, period)

        if len(filtered_hits) >= 6:
            redisServer.clearUserSearch(user)
            print(maxScore)
            if maxScore > 100:
                answer = filtered_hits[0]['_source']['question'] + '\n' \
                          + filtered_hits[0]['_source']['answer'] + '\n' \
                          + "<a href=\"" + filtered_hits[0]['_source']['href'] + "\">【知识来源:段涛大夫" + \
                          filtered_hits[0]['_source']['title'] + "】</a>"
                print(answer)
                self.wechat.send_text_message(user, answer)
                content = replyConfig['interesting'] + "\n" \
                          + '1.' + filtered_hits[1]['_source']['question'] + '\n' \
                          + '2.' + filtered_hits[2]['_source']['question'] + '\n' \
                          + '3.' + filtered_hits[3]['_source']['question'] + '\n' \
                          + '4.' + filtered_hits[4]['_source']['question'] + "\n" \
                          + '5.' + filtered_hits[5]['_source']['question'] + "\n" \
                          + "(若是，请输入问题前面的数字)"
                for i in range(1, 6):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question']
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])

            else:
                content = replyConfig['exist'] + "\n" \
                          + '1.' + filtered_hits[0]['_source']['question'] + '\n' \
                          + '2.' + filtered_hits[1]['_source']['question'] + '\n' \
                          + '3.' + filtered_hits[2]['_source']['question'] + '\n' \
                          + '4.' + filtered_hits[3]['_source']['question'] + "\n" \
                          + '5.' + filtered_hits[4]['_source']['question'] + "\n" \
                          + "(若是，请输入问题前面的数字)"
                for i in range(0, 5):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question']
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])

        elif len(filtered_hits) > 0:
            redisServer.clearUserSearch(user)
            if maxScore > 100:
                answer = filtered_hits[0]['_source']['question'] + '\n' \
                          + filtered_hits[0]['_source']['answer'] + '\n' \
                          + "<a href=\"" + filtered_hits[0]['_source']['href'] + "\">【知识来源:段涛大夫" + \
                          filtered_hits[0]['_source']['title'] + "】</a>"

                self.wechat.send_text_message(user, answer)
                content = replyConfig['interesting'] + "\n"
                index = 1
                for index in range(1,len(filtered_hits)):
                    content = content + str(index) + '.' + filtered_hits[index]['_source']['question'] + "\n"
                    index += 1
                content = content + "(若是，请输入问题前面的数字)"
                for i in range(1, len(filtered_hits)):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question']
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])
            else:
                content = replyConfig['exist'] + "\n"
                index = 1
                for filtered_hit in filtered_hits:
                    content = content + str(index) + '.' + filtered_hit['_source']['question'] + "\n"
                    index += 1
                content = content + "(若是，请输入问题前面的数字)"
                for i in range(0, len(filtered_hits)):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question']
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])
        else:
            content = replyConfig['not_found']
            result = False
        return content, result

    # say hello at first time
    def sayHello(self, user, today, createdTime):
        os.environ['TZ'] = 'Asia/Shanghai'
        time.tzset()
        now = time.localtime(createdTime)
        saidHello = False
        if not redisServer.ifUserLogged(today, user):
            welcomeWord = self.setWelcomeWord(createdTime)
            self.wechat.send_text_message(user, welcomeWord)
            saidHello = True

        redisServer.setUser(today, user)
        return saidHello

    def setWelcomeWord(self, createdTime):
        welcomeWord = " "
        os.environ['TZ'] = 'Asia/Shanghai'
        time.tzset()
        now = time.localtime(createdTime)

        if now.tm_hour < 12:
            welcomeWord = replyConfig["morning"]
        if now.tm_hour == 12:
            welcomeWord = replyConfig["noon"]
        if 18 > now.tm_hour > 12:
            welcomeWord = replyConfig["afternoon"]
        if now.tm_hour >= 18:
            welcomeWord = replyConfig["evening"]

        return welcomeWord
