import re, json
from util.pre import process

def findGreeting(question):
    question = question.strip()
    source = ["您好","你好","Hello","hello","Hi","hi","hey","Hey","HEY","HI"]
    if question in source:
        return True
    else:
        return False

def findThanks(question):
    question = question.strip()
    return bool(re.search("^谢谢.*",question))


def handleQuestion(question):
    question_sequence = ''
    period = ''
    isSub = False

    question_tmp = re.sub(r'怀孕|孕期|孕妇|什么', '', question)
    if len(question_tmp) > 0:
        question = question_tmp
    if len(question_tmp) == len(question):
        isSub = True

    # question = [word for word, flag in posseg.cut(question) if flag != 'a' and flag != 'd']
    # question = ''.join(question)
    # print("question:", question)

    question_filted = re.sub(r'注意事项|不是|新生儿|比较好|可以|吗|咋|怎么办|如何|怎么|哪些|会|和|能|或|有|怎么样|要不要|还|了|很|有点|都|厉害|严重|稍微|有一点|，|,|。', '',
                             question)
    question_sequence, period = process(question_filted)
    print("question", question_sequence)
    return (question_sequence, question, period, isSub)


def filter_list(list, period, maxScore):
    filtered_hits = []
    for el in list:
        if el['_score'] > 20 and el['_score'] > 0.1 * maxScore:
            if period == u"无":
                filtered_hits.append(el)
            else:
                if el['_source']['period'] == period:
                    filtered_hits.append(el)
    return filtered_hits


def afterSearch(res, period):
    # filterResult
    maxScore = res['hits']['max_score']
    took = res['took']
    all_hits = res['hits']['hits']
    filtered_hits = filter_list(all_hits, period, maxScore)

    return filtered_hits, maxScore, took

def getReply(*texts):
    reply=''
    if len(texts) == 4:
        question = texts[0]
        answer = texts[1]
        href = texts[2]
        title = texts[3]
        reply = question + '\n' + answer + '\n' + "<a href=\"" + href + "\">【知识来源:段涛大夫" + title + "】</a>"
        while len(reply.encode("utf-8")) > 2000:
            answer = answer[0:-3]+"……"
            reply = question + '\n' + answer + '\n' + "<a href=\"" + href + "\">【知识来源:段涛大夫" + title + "】</a>"

    elif len(texts) == 2:
        question = texts[0]
        answer = texts[1]
        reply = question + '\n' + answer
        while len(reply.encode("utf-8")) > 2000:
            answer = answer[0:-3] + "……"
            reply = question + '\n' + answer + '\n'

    elif len(texts) == 1:
        answer = texts[0]
        reply = answer
        while len(reply.encode("utf-8")) > 1500:
            answer = answer[0:-3] + "……"
            reply = answer

    return reply


