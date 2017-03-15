import os
import os.path
import re
from collections import defaultdict

def beforProcess():
    month = input("Enter the month: ")
    if int(month) > 12 and int(month) < 1:
        print("Wrong input")
        return
    if len(month) < 2:
        month = "0" + month
    day = int(input("Enter the day: "))
    return month, day

def logFiles(rootdir):
    files = []
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            files.append(os.path.join(parent, filename))
    return files

def getOneDayLog(files, month, day):
    d = defaultdict(list)
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                date = line[0:10]
                re_result = re.search("2017-(.*?)-(.*?) ", line)
                log_month = int(re_result.group(1))
                log_day = int(re_result.group(2))
                search = re.search("SEARCH\[(.*?)\]", line).group(1)
                result = re.search("RESULT\[(.*?)\]", line).group(1)
                if int(month) == log_month and int(day) == log_day:
                    d[search].append(result)
        f.closed
    getResult(d, month, day)

def getResult(loglist,month,day):
    suc_questions = []
    fail_questions = []
    suc_count = 0
    fail_count = 0
    all_count = 0

    for k, v in loglist.items():
        for time in v:
            all_count = all_count +len(v)
        print(all_count)
        if v[0] == "True":
            suc_questions.append(k)
            suc_count = suc_count + len(v)
        else:
            fail_questions.append(k)
            fail_count =fail_count + len(v)

    f = open('result.log', 'w')
    f.write("2017-" + str(month) + "-" + str(day)+"\n")
    f.write("匹配率："+str(suc_count/all_count*100)+"%\n")
    f.write("总搜索数:"+str(all_count)+" ,成功匹配:"+str(suc_count)+" ,未匹配:"+str(fail_count)+"\n\n")
    f.write("未成功匹配问题:"+"\n")
    for fail_question in fail_questions:
        f.write(fail_question+"\n")
    f.write("\n")
    f.write("成功匹配问题:"+"\n")
    for suc_question in suc_questions:
        f.write(suc_question+"\n")


if __name__ == "__main__":
    month, day= beforProcess()
    rootdir = "./log_server"  # log directory
    files = logFiles(rootdir)
    getOneDayLog(files, month, day)

