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
from util.util import handleQuestion, afterSearch, findGreeting, getReply,findThanks
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
        print("<New message>")
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
                        # try:
                        #     self.wechat.send_text_message(user, self.setWelcomeWord(createdTime))
                        # except:
                        #     pass
                        reply = self.setWelcomeWord(createdTime) + "！" + replyConfig["greeting"]
                    if findThanks(content):
                        reply = replyConfig["nothanks"]
                    else:
                        reply, answerID, maxScore, questionIDs = self.searchQuestion(user, content)
                        # log_server
                        log.writeLog(user, content, answerID, maxScore, questionIDs)

                resp.status = falcon.HTTP_200
                resp.body = self.wechat.response_text(content=reply)

            elif isinstance(self.wechat.message, EventMessage):
                if self.wechat.message.type == 'subscribe':
                    if not redisServer.ifUserLogged(today, user):
                        redisServer.setUser(today, user)
                    # try:
                    #     self.wechat.send_text_message(user, replyConfig['welcome'])
                    # except:
                    #     pass
                    resp.status = falcon.HTTP_200
                    reply = replyConfig['welcome'] + "\n" + replyConfig['welcome2']
                    resp.body = self.wechat.response_text(content=reply)
            else:
                resp.status = falcon.HTTP_200
                reply = replyConfig['not_found']
                resp.body = self.wechat.response_text(content=reply)
        except ParseError:

            resp.status = falcon.HTTP_200
            resp.body = ""

    def searchQuestion(self, user, question):
        questionIDs = []
        answerID = None
        bar = 100
        # handleQuestion
        (question_sequence, question, period, isSub) = handleQuestion(question)
        if isSub:
            bar = 90
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
            if maxScore > bar:
                print(filtered_hits[0]['_source'])
                if filtered_hits[0]['_source']['href'] != None:
                    answer = getReply(filtered_hits[0]['_source']['answer']) + '\n' \
                         + "<a href=\"" + filtered_hits[0]['_source']['href'] + "\">【知识来源:段涛大夫" + \
                         filtered_hits[0]['_source']['title'] + "】</a>"
                else:
                    answer = getReply(filtered_hits[0]['_source']['answer']) + '\n' \
                    + "【知识来源:段涛大夫" + filtered_hits[0]['_source']['title'] + "】"
                answerID = filtered_hits[0]['_id']
                # try:
                #     self.wechat.send_text_message(user, answer)
                # except:
                #     pass
                content = answer + "\n\n" \
                          + replyConfig['interesting'] + "\n" \
                          + '1.' + filtered_hits[1]['_source']['question'].strip() + '\n' \
                          + '2.' + filtered_hits[2]['_source']['question'].strip() + '\n' \
                          + '3.' + filtered_hits[3]['_source']['question'].strip() + '\n' \
                          + '4.' + filtered_hits[4]['_source']['question'].strip() + "\n" \
                          + '5.' + filtered_hits[5]['_source']['question'].strip() + "\n" \
                          + "(若是，请输入问题前面的数字)"
                for i in range(1, 6):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question'].strip()
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])
                    questionIDs.append(filtered_hits[i]['_id'])

            else:
                content = replyConfig['exist'] + "\n" \
                          + '1.' + filtered_hits[0]['_source']['question'].strip() + '\n' \
                          + '2.' + filtered_hits[1]['_source']['question'].strip() + '\n' \
                          + '3.' + filtered_hits[2]['_source']['question'].strip() + '\n' \
                          + '4.' + filtered_hits[3]['_source']['question'].strip() + "\n" \
                          + '5.' + filtered_hits[4]['_source']['question'].strip() + "\n" \
                          + "(若是，请输入问题前面的数字)"
                for i in range(0, 5):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question'].strip()
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])
                    questionIDs.append(filtered_hits[i]['_id'])
        elif len(filtered_hits) == 1:
            redisServer.clearUserSearch(user)
            if maxScore > bar:
                if filtered_hits[0]['_source']['href'] != None:
                    content = getReply(filtered_hits[0]['_source']['answer']) + '\n' \
                          + "<a href=\"" + filtered_hits[0]['_source']['href'] + "\">【知识来源:段涛大夫" + \
                          filtered_hits[0]['_source']['title'] + "】</a>"
                else:
                    content = getReply(filtered_hits[0]['_source']['answer']) + '\n' \
                          + "【知识来源:段涛大夫" + filtered_hits[0]['_source']['title'] + "】"
                answerID = filtered_hits[0]['_id']
            else:
                content = replyConfig['exist'] + "\n"
                index = 1
                for filtered_hit in filtered_hits:
                    content = content + str(index) + '.' + filtered_hit['_source']['question'].strip() + "\n"
                    index += 1
                content = content + "(若是，请输入问题前面的数字)"
                for i in range(0, len(filtered_hits)):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question'].strip()
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])
                    questionIDs.append(filtered_hits[i]['_id'])

        elif len(filtered_hits) > 0:
            redisServer.clearUserSearch(user)
            if maxScore > bar:
                print(filtered_hits[0]['_source'])
                if filtered_hits[0]['_source']['href'] != None:
                    answer = getReply(filtered_hits[0]['_source']['answer']) + '\n' \
                         + "<a href=\"" + filtered_hits[0]['_source']['href'] + "\">【知识来源:段涛大夫" + \
                         filtered_hits[0]['_source']['title'] + "】</a>"
                else:
                    answer = getReply(filtered_hits[0]['_source']['answer']) + '\n' \
                         + "【知识来源:段涛大夫" + filtered_hits[0]['_source']['title'] + "】"
                answerID = filtered_hits[0]['_id']
                # try:
                #     self.wechat.send_text_message(user, answer)
                # except:
                #     pass
                content = answer + "\n\n" + replyConfig['interesting'] + "\n"
                index = 1
                for index in range(1, len(filtered_hits)):
                    content = content + str(index) + '.' + filtered_hits[index]['_source']['question'].strip() + "\n"
                    index += 1
                content = content + "(若是，请输入问题前面的数字)"
                for i in range(1, len(filtered_hits)):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question'].strip()
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])
                    questionIDs.append(filtered_hits[i]['_id'])
            else:
                content = replyConfig['exist'] + "\n"
                index = 1
                for filtered_hit in filtered_hits:
                    content = content + str(index) + '.' + filtered_hit['_source']['question'].strip() + "\n"
                    index += 1
                content = content + "(若是，请输入问题前面的数字)"
                for i in range(0, len(filtered_hits)):
                    redisServer.setUserSearch(user, filtered_hits[i]['_source']['question'].strip()
                                              , filtered_hits[i]['_source']['answer']
                                              , filtered_hits[i]['_source']['title']
                                              , filtered_hits[i]['_source']['href'])
                    questionIDs.append(filtered_hits[i]['_id'])
        else:
            content = replyConfig['not_found']
        return content, answerID, maxScore, questionIDs

    # say hello at first time
    def sayHello(self, user, today, createdTime):
        os.environ['TZ'] = 'Asia/Shanghai'
        time.tzset()
        now = time.localtime(createdTime)
        saidHello = False
        if not redisServer.ifUserLogged(today, user):
            welcomeWord = self.setWelcomeWord(createdTime)
            try:
                self.wechat.send_text_message(user, welcomeWord)
            except:
                pass
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
