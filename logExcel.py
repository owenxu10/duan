import os
import os.path
import re
from openpyxl import Workbook
from openpyxl.styles import Border, Side, PatternFill
import json
from elasticsearch import Elasticsearch


def style_range(ws):
    border = Border(left=Side(style='thin', color='FF99C4E6'),
                    right=Side(style='thin', color='FF99C4E6'),
                    top=Side(style='thin', color='FF99C4E6'),
                    bottom=Side(style='thin', color='FF99C4E6'))

    fill = PatternFill("solid", fgColor="f9fbfd")
    for row in range(1, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            ws.cell(column=col, row=row).border = border
            ws.cell(column=col, row=row).fill = fill


def logFiles(rootdir):
    files = []
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            files.append(os.path.join(parent, filename))
    return files


def getSearchResult(answer, questions):
    es = Elasticsearch()
    searchResult = ''
    if len(answer) != 0:
        query = {
            "query": {
                "terms": {
                    "_id": [answer]
                }
            }
        }

        res = es.search(index="qa_demo", body=json.dumps(query, ensure_ascii=False))
        searchResult = res['hits']['hits'][0]['_source']['answer'] + '\n\n'

    if len(questions) != 0:
        question = questions.split('|')
        query = {
            "query": {
                "terms": {
                    "_id": question
                }
            }
        }

        res = es.search(index="qa_demo", body=json.dumps(query, ensure_ascii=False))
        hits = res['hits']['hits']
        for i in range(0, len(hits)):
            searchResult = searchResult + str(i + 1) + '.' + hits[i]['_source']['question'] + '\n'

    return searchResult


def readLogs(files):
    currentDate = ''
    answer = ''
    c_count = c_suc = c_fail = 0
    l_count = l_suc = l_fail = 0
    ll_suc = []
    ll_suc_answer = []
    ll_suc_questions = []
    ll_fail = []
    currentDate = 0
    wb = Workbook()
    ws = wb.active
    ws.title = "Overview"
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                date = line[0:10]
                re_result = re.search("2017-(.*?)-(.*?) ", line)
                log_month = int(re_result.group(1))
                log_day = int(re_result.group(2))
                search = re.search("SEARCH\[(.*?)\]", line).group(1)
                answer_group = re.search("ANSWER\[(.*?)\]", line)
                if answer_group is not None:
                    answer = answer_group.group(1)
                questions_group = re.search("RESULT\[(.*?)\]", line)
                if questions_group is not None:
                    questions = questions_group.group(1)

                if date != currentDate and currentDate != 0:
                    # Write
                    ws = wb.create_sheet(title=currentDate)

                    ws['A1'] = "当日搜索次数:" + str(l_count)
                    ws['A2'] = "成功匹配:" + str(l_suc)
                    ws['C2'] = "未成功匹配:" + str(l_fail)
                    ws['B2'] = "匹配率:" + str(l_suc / l_count * 100) + "%"

                    ws['A3'] = "成功匹配问题"
                    ws['B3'] = "匹配结果"
                    ws['C3'] = "未成功匹配问题"

                    for i in range(0, len(ll_suc)):
                        ws.cell(column=1, row=i + 4).value = ll_suc[i]

                        result = getSearchResult(ll_suc_answer[i], ll_suc_questions[i])
                        ws.cell(column=2, row=i + 4).value = result
                    for i in range(0, len(ll_fail)):
                        ws.cell(column=3, row=i + 4).value = ll_fail[i]

                    style_range(ws)
                    # Clear
                    l_count = l_suc = l_fail = 0
                    ll_suc.clear()
                    ll_fail.clear()

                c_count += 1
                l_count += 1
                currentDate = date
                if len(answer) != 0 and len(questions) != 0:
                    c_suc += 1
                    l_suc += 1
                    ll_suc.append(search)
                    ll_suc_answer.append(answer)
                    ll_suc_questions.append(questions)
                else:
                    c_fail += 1
                    l_fail += 1
                    ll_fail.append(search)

    ws = wb.create_sheet(title=currentDate)

    ws['A1'] = "当日搜索次数:" + str(l_count)
    ws['A2'] = "成功匹配:" + str(l_suc)
    ws['C2'] = "未成功匹配:" + str(l_fail)
    ws['B2'] = "匹配率:" + str(l_suc / l_count * 100) + "%"

    ws['A3'] = "成功匹配问题"
    ws['B3'] = "匹配结果"
    ws['C3'] = "未成功匹配问题"

    for i in range(0, len(ll_suc)):
        ws.cell(column=1, row=i + 4).value = ll_suc[i]

        result = getSearchResult(ll_suc_answer[i], ll_suc_questions[i])
        ws.cell(column=2, row=i + 4).value = result
    for i in range(0, len(ll_fail)):
        ws.cell(column=3, row=i + 4).value = ll_fail[i]

    style_range(ws)

    overview = wb["Overview"]
    overview['A1'] = "所有搜索次数:" + str(c_count)
    overview['A2'] = "成功匹配:" + str(c_suc)
    overview['A3'] = "未成功匹配:" + str(c_fail)
    overview['A4'] = "匹配率:" + str(c_suc / c_count * 100) + "%"

    dest_filename = 'log.xlsx'
    style_range(overview)
    wb.save(filename=dest_filename)


if __name__ == "__main__":
    wb = Workbook()
    rootdir = "./test_log"  # log directory
    files = logFiles(rootdir)
    readLogs(files)
