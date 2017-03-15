#coding=utf8
def process(question):
	peiriods = ['产后','备孕','孕期','临产','新生儿','流产']
	peiriod = '无'
	for t in peiriods:
		if t in question:
			peiriod = t

	sen = question
	with open('util/dict') as file:
		for line in file:
			if line.split()[0] in question:
				sen = question.replace(line.split()[0],line.split()[1])

	return (sen,peiriod)
