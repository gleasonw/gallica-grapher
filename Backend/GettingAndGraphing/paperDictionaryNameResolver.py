import concurrent.futures
from requests_toolbelt import sessions
from math import ceil
import csv
from lxml import etree
from Backend.GettingAndGraphing.termSearch import TimeoutAndRetryHTTPAdapter


def standardizeDateRange(dateRangeToStandardize):
	splitDates = dateRangeToStandardize.split("-")
	try:
		for i in range(len(splitDates)):
			int(splitDates[i])
		if len(splitDates) == 2:
			return "{0}-{1}".format(splitDates[0], splitDates[1])
		else:
			return splitDates[0]
	except ValueError:
		return None


class paperGetter:

	def __init__(self, query, session):
		self.query = query
		self.session = session
		pass

	def makeCSVwithCleanDates(self):
		cleanFileName = "paperDictionaryWithoutFunkyDates.csv"
		with open("../Postgre/paperDictionaryWithFunkyDates.csv", "r", encoding="utf8") as inFile:
			reader = csv.reader(inFile)
			next(reader)
			with open(cleanFileName, "w", encoding="utf8") as outFile:
				writer = csv.writer(outFile)
				writer.writerow(["journal", "startDate","endDate", "url", "code"])
				for newsData in reader:
					publicationRange = newsData[1]
					standardizedRange = standardizeDateRange(publicationRange)
					if standardizedRange is None:
						continue
					else:
						checkedRange = standardizedRange
						checkedRange = checkedRange.split("-")
						paperName = newsData[0]
						paperName = paperName.replace('"', '')
						paperName = paperName.replace(']', '')
						paperName = paperName.replace('[', '')
						paperUrl = newsData[2]
						paperCode = newsData[3]
						paperCode = paperCode + "_date"
						if len(checkedRange) == 1:
							endDate = checkedRange[0]
						else:
							endDate = checkedRange[1]
						writer.writerow([paperName, checkedRange[0], endDate, paperUrl, paperCode])



	def makeBetterDictionary(self):
		parameters = dict(version=1.2, operation="searchRetrieve", exactSearch=False, collapsing=True,
						  query=self.query, startRecord=0, maximumRecords=1)
		response = self.session.get("", params=parameters)
		root = etree.fromstring(response.content)
		numberHits = int(root[2].text)
		iterations = ceil(numberHits / 50)
		startRecordList = []
		resultList = []
		for i in range(iterations):
			startRecordList.append((i * 50) + 1)
		with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
			for i, result in enumerate(executor.map(self.gatherPapers, startRecordList), 1):
				resultList.extend(result)

		with open("../Postgre/paperDictionaryWithFunkyDates.csv", "w", encoding="utf8") as outFile:
			writer = csv.writer(outFile)
			writer.writerow(["journal", "date", "url", "code"])
			for entry in resultList:
				writer.writerow(entry)

	def gatherPapers(self, startRecord):
		gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
		adapter = TimeoutAndRetryHTTPAdapter(timeout=2.5)
		gallicaHttpSession.mount("https://", adapter)
		gallicaHttpSession.mount("http://", adapter)
		parameters = dict(version=1.2, operation="searchRetrieve", exactSearch=False, collapsing=True,
						  query=self.query, startRecord=startRecord, maximumRecords=50)
		response = gallicaHttpSession.get("https://gallica.bnf.fr/SRU", params=parameters)
		root = etree.fromstring(response.content)
		results = []
		for queryHit in root.iter("{http://www.loc.gov/zing/srw/}record"):
			data = queryHit[2][0]
			try:
				journalName = data.find('{http://purl.org/dc/elements/1.1/}title').text
			except AttributeError:
				continue
			try:
				journalUrl = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
			except AttributeError:
				journalUrl = None
			try:
				journalDate = data.find('{http://purl.org/dc/elements/1.1/}date').text
			except AttributeError:
				journalDate = None
			if journalUrl is not None:
				journalCode = journalUrl[-16:-5]
			else:
				journalCode = None
			print([journalName, journalDate, journalUrl, journalCode])
			results.append([journalName, journalDate, journalUrl, journalCode])
		return results

	def renamePapersToTheNameThatShowsUpInResult(self):
		with open("paperDictionaryWithoutFunkyDates.csv", "r", encoding="utf8") as inFile:
			reader = csv.reader(inFile)
			with open("../Postgre/paperDictionaryGoodDatesGoodNames.csv", "w", encoding="utf8") as outFile:
				writer = csv.writer(outFile)
				next(reader)
				with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
					for result in executor.map(self.getTheNames, reader):
						if result:
							writer.writerow(result)


	def getTheNames(self, newspaper):
		if newspaper:
			query = 'arkPress all "{0}" sortby dc.date/sort.ascending '
			gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
			adapter = TimeoutAndRetryHTTPAdapter(timeout=2.5)
			gallicaHttpSession.mount("https://", adapter)
			gallicaHttpSession.mount("http://", adapter)
			newspaperCode = newspaper[4]
			newspaperQuery = query.format(newspaperCode)
			parameters = dict(version=1.2, operation="searchRetrieve", exactSearch=False, collapsing=False,
							  query=newspaperQuery, startRecord=0, maximumRecords=1)
			response = gallicaHttpSession.get("",params=parameters)
			root = etree.fromstring(response.content)
			try:
				queryHit = root[4][0]
				data = queryHit[2][0]
				journalName = data.find('{http://purl.org/dc/elements/1.1/}title').text
				print([journalName, newspaper[1], newspaper[2], newspaper[3], newspaper[4]])
				return [journalName, newspaper[1], newspaper[2], newspaper[3], newspaper[4]]
			except IndexError:
				return
			# queryHit = root.find("{http://www.loc.gov/zing/srw/}record")

		else:
			return


if __name__ == "__main__":
	gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
	adapter = TimeoutAndRetryHTTPAdapter(timeout=2.5)
	gallicaHttpSession.mount("https://", adapter)
	gallicaHttpSession.mount("http://", adapter)
	paperEditor = paperGetter("neat", gallicaHttpSession)
	paperEditor.renamePapersToTheNameThatShowsUpInResult()