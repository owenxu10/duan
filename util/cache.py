from redis import StrictRedis


class redisServer:
    r = StrictRedis(host='127.0.0.1', port='6379', db=0)

    @classmethod
    def setUser(cls, date, user):
        cls.r.sadd(date, user)

    @classmethod
    def ifUserLogged(cls, date, user):
        return cls.r.sismember(date, user)

    @classmethod
    def setUserSearch(cls, user, question, answer, title, href):
        cls.r.rpush(user + "question", question)
        cls.r.rpush(user + "answer", answer)
        cls.r.rpush(user + "title", title)
        cls.r.rpush(user + "href", href)

    @classmethod
    def getQuestionLength(cls, user):
        return cls.r.llen(user + "question")

    @classmethod
    def getQuestion(cls, user, index):
        return cls.r.lindex(user + "question", index)

    @classmethod
    def getAnswer(cls, user, index):
        return cls.r.lindex(user + "answer", index)

    @classmethod
    def getTitle(cls, user, index):
        return cls.r.lindex(user + "title", index)

    @classmethod
    def getHref(cls, user, index):
        return cls.r.lindex(user + "href", index)

    @classmethod
    def clearUserSearch(cls, user):
        cls.r.delete(user + "question")
        cls.r.delete(user + "answer")
        cls.r.delete(user + "title")
        cls.r.delete(user + "href")
