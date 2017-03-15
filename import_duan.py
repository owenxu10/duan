# encoding:utf8
import elasticsearch

es = elasticsearch.Elasticsearch()

import json
import re

articles = json.load(open('duan.json'))
for a in articles:
    if re.match(r'院长日记', a['title']):
        continue
    if re.match(r'Tony日记', a['title']):
        continue
    if re.match(r'产科那些事', a['title']):
        continue
    if len(a['content'])<80:
        continue
    es.index('qa_demo', 'qa', body={
        "question": a['title'],
        "answer": a['content'],
        "href": a['href'],
        'title': None
    })
