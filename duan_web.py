import falcon
import json
from elasticsearch import Elasticsearch

from util.util import afterSearch, handleQuestion


class duanWeb(object):
    def __init__(self):
        self.es = Elasticsearch()

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = "Success"

    def on_post(self, req, resp):
        json_data = json.loads(str(req.stream.read().decode("utf-8")))
        question = json_data['question']
        results = ''
        # handleQuestion
        (question_sequence, question, period,isSub) = handleQuestion(question)

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
        # print("res", res)
        results, maxScore, took = afterSearch(res, period)
        hits = self.convert2Json(results, took)
        resp.status = falcon.HTTP_200
        resp.body = hits

    def convert2Json(self, results, took):

        json_data = {
            "took": took,
            "hits": [results[i] for i in range(0, len(results))]
        }

        return json.dumps(json_data)
