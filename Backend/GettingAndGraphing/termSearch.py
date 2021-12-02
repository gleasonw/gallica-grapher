import csv
import shutil
import os
import concurrent.futures
from math import ceil

from requests_toolbelt import sessions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from Backend.GettingAndGraphing.batchGetter import GallicaHunter
from Backend.GettingAndGraphing.dictionaryMaker import DictionaryMaker

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


class GallicaSearch:

	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, progressTrackerThread, **kwargs):
		self.lowYear = None
		self.highYear = None
		self.isYearRange = None
		self.baseQuery = None
		self.progressTrackerThread = progressTrackerThread
		self.strictYearRange = strictYearRange
		self.totalResults = 0
		self.discoveryProgressPercent = 0
		self.retrievalProgressPercent = 0
		self.progressIterations = 0
		self.newspaper = newspaper
		self.newspaperDictionary = {}
		self.chunkedNewspaperDictionary = {}
		self.collectedQueries = []
		self.searchTerm = searchTerm
		self.topTenPapers = []
		self.numResultsForEachPaper = {}
		self.establishYearRange(yearRange)
		self.parseNewspaperDictionary()
		self.establishStrictness()
		self.buildQuery()
		self.listOfAllQueryStrings = []

		self.paperNameCounts = []

		self.fileName = self.determineFileName()

	def checkIfFileAlreadyInDirectory(self):
		return os.path.isfile(os.path.join("../CSVdata", self.fileName))

	def runQuery(self):
		self.findTotalResults()
		self.runSearch()

	def getTopTenPapers(self):
		return self.topTenPapers

	def getFileName(self):
		return self.fileName

	def getSearchTerm(self):
		return self.searchTerm

	def getYearRange(self):
		return "{0}-{1}".format(self.lowYear, self.highYear)

	def getCollectedQueries(self):
		return self.collectedQueries

	def getDiscoveryProgressPercent(self):
		return self.discoveryProgressPercent

	def getRetrievalProgressPercent(self):
		return self.retrievalProgressPercent

	@staticmethod
	def makeSession():
		gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
		adapter = TimeoutAndRetryHTTPAdapter(timeout=5)
		gallicaHttpSession.mount("https://", adapter)
		gallicaHttpSession.mount("http://", adapter)
		return gallicaHttpSession

	@staticmethod
	def sendQuery(queryToSend, **kwargs):
		session = GallicaSearch.makeSession()
		if kwargs['startRecord'] is None:
			startRecord = 1
		else:
			startRecord = kwargs['startRecord']
		if kwargs['numRecords'] is None:
			numRecords = 50
		else:
			numRecords = kwargs['numRecords']
		hunter = GallicaHunter(queryToSend, startRecord, numRecords, session)
		hunter.hunt()
		return hunter

	def packageQuery(self):
		if len(self.collectedQueries) != 0:
			self.makeCSVFile()
		else:
			pass

	def makeCSVFile(self):
		with open(self.fileName, "w", encoding="utf8", newline='') as outFile:
			writer = csv.writer(outFile)
			writer.writerow(["date", "journal", "url"])
			for csvEntry in self.collectedQueries:
				writer.writerow(csvEntry)
		shutil.move(self.fileName, os.path.join("../CSVdata", self.fileName))

	def determineFileName(self):
		nameOfFile = ''
		if self.newspaper == "all":
			nameOfFile = self.searchTerm + "-all-"
		else:
			for paper in self.newspaper:
				paper = paper[0:5]
				nameOfFile = nameOfFile + paper + "-"
			nameOfFile = nameOfFile[0:len(nameOfFile) - 2]
			wordsInQuery = self.searchTerm.split(" ")
			for word in wordsInQuery:
				nameOfFile = nameOfFile + word
		if self.isYearRange:
			nameOfFile = nameOfFile + str(self.lowYear) + "." + str(self.highYear)
		nameOfFile = nameOfFile + ".csv"
		return nameOfFile

	# Good time to parse errors in formatting too
	def establishStrictness(self):
		if self.strictYearRange in ["ya", "True", "true", "yes", "absolutely"]:
			self.strictYearRange = True
		else:
			self.strictYearRange = False

	def checkIfHitDateinQueryRange(self, dateToCheck):
		yearList = dateToCheck.split("-")
		lower = int(yearList[0])
		higher = int(yearList[1])
		if lower < self.lowYear and higher > self.highYear:
			return True
		else:
			return False

	# What if list of papers?
	def parseNewspaperDictionary(self):
		dicParser = DictionaryMaker(self.newspaper, [self.lowYear, self.highYear], self.strictYearRange)
		self.newspaperDictionary = dicParser.getDictionary()

	def establishYearRange(self, yearRange):
		if len(yearRange) == 2:
			self.lowYear = int(yearRange[0])
			self.highYear = int(yearRange[1])
			self.isYearRange = True
		else:
			self.isYearRange = False

	def buildQuery(self):
		if self.isYearRange:
			if self.newspaper[0] == "noDict":
				self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and (gallica adj "{' \
								 '{searchWord}}") sortby dc.date/sort.ascending '
			else:
				self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and ((arkPress all "{{{{' \
								 'newsKey}}}}") and (gallica adj "{{searchWord}}")) sortby dc.date/sort.ascending '
			self.baseQuery = self.baseQuery.format(firstYear=str(self.lowYear), secondYear=str(self.highYear))
		else:
			if self.newspaper[0] == "noDict":
				self.baseQuery = '(gallica adj "{searchWord}") and (dc.type all "fascicule") sortby dc.date/sort.ascending'
			else:
				self.baseQuery = 'arkPress all "{{newsKey}}" and (gallica adj "{searchWord}") sortby dc.date/sort.ascending'
		self.baseQuery = self.baseQuery.format(searchWord=self.searchTerm)

	def runSearch(self):
		pass

	def findTotalResults(self):
		pass

	def generateNewspaperDictionary(self):
		self.newspaperDictionary.clear()
		for nameCountCode in self.paperNameCounts:
			paperName = nameCountCode[0]
			paperCount = nameCountCode[1]
			paperCode = nameCountCode[2]
			self.newspaperDictionary.update({paperName: paperCode})
			self.numResultsForEachPaper.update({paperName: paperCount})
			# A little weird to calculate total results here
			self.sumUpTotalResults(paperCount)
	#Might be a little slow
	def updateNewspaperCountDictionary(self):
		currentCount = 0
		for newspaper in self.newspaperDictionary:
			for result in self.collectedQueries:
				paperName = result[1]
				if paperName == newspaper:
					currentCount += 1
			self.updateTopTenPapers(newspaper, currentCount)
			self.numResultsForEachPaper.update({newspaper: currentCount})
			currentCount = 0

	def updateTopTenPapers(self, name, count):
		if not self.topTenPapers:
			self.topTenPapers.append([name, count])
			return
		elif len(self.topTenPapers) < 10:
			iterations = len(self.topTenPapers)
		else:
			iterations = 10
		for i in range(iterations):
			currentIndexCount = self.topTenPapers[i][1]
			if count > currentIndexCount:
				self.topTenPapers.insert(i, [name, count])
				del (self.topTenPapers[10:])
				return

	def sumUpTotalResults(self, toAdd):
		self.totalResults = self.totalResults + toAdd

	def updateDiscoveryProgressPercent(self, iteration, total):
		self.discoveryProgressPercent = int((iteration / total) * 100)
		self.progressTrackerThread.setDiscoveryProgress(self.discoveryProgressPercent)

	def updateRetrievalProgressPercent(self, iteration, total):
		self.retrievalProgressPercent = int((iteration / total) * 100)
		self.progressTrackerThread.setRetrievalProgress(self.retrievalProgressPercent)


class FullSearchWithinDictionary(GallicaSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, progressTracker):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange, progressTracker)

	def runSearch(self):
		self.createQueryStringList()
		self.createWorkersForSearch()
		self.updateNewspaperCountDictionary()
		self.progressTrackerThread.setNumberRetrievedResults(len(self.collectedQueries))
		self.packageQuery()

	def createQueryStringList(self):
		for newspaper in self.newspaperDictionary:
			hitsInNewspaper = self.numResultsForEachPaper[newspaper]
			newspaperKey = self.newspaperDictionary[newspaper]
			numberOfQueriesToSend = ceil(hitsInNewspaper / 50)
			queryFormatForPaper = self.baseQuery.format(newsKey=newspaperKey)
			startRecord = 1
			for i in range(numberOfQueriesToSend):
				queryRecordPair = [queryFormatForPaper, startRecord]
				self.listOfAllQueryStrings.append(queryRecordPair)
				startRecord += 50

	def createWorkersForSearch(self):
		progress = 0
		with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
			for result in executor.map(self.sendWorkersToSearch, self.listOfAllQueryStrings):
				numberResultsInBatch = len(result)
				self.collectedQueries.extend(result)
				progress = progress + numberResultsInBatch
				self.updateRetrievalProgressPercent(progress, self.totalResults)
			self.updateRetrievalProgressPercent(100, 100)

	def sendWorkersToSearch(self, queryAndRecordStart):
		query = queryAndRecordStart[0]
		recordStart = queryAndRecordStart[1]
		session = GallicaSearch.makeSession()
		hunterForQuery = GallicaHunter(query, recordStart, 50, session)
		hunterForQuery.hunt()
		results = hunterForQuery.getResultList()
		return results

	def findTotalResults(self):
		self.createWorkersForFindingTotalResults()
		self.progressTrackerThread.setDiscoveredResults(self.totalResults)

	def createWorkersForFindingTotalResults(self):
		try:
			with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
				for i, result in enumerate(executor.map(self.findNumberResults, self.newspaperDictionary), 1):
					if result:
						self.paperNameCounts = self.paperNameCounts + result
					else:
						print("WORTHLESS")
					self.updateDiscoveryProgressPercent(i, len(self.newspaperDictionary))
			self.generateNewspaperDictionary()
		except Exception as error:
			print(error)
			raise

	def findNumberResults(self, newspaper):
		session = GallicaSearch.makeSession()
		paperCounts = []
		newspaperCode = self.newspaperDictionary[newspaper]
		newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
		hunterForTotalNumberOfQueryResults = GallicaHunter(newspaperQuery, 1, 1, session)
		numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
		if numberResultsForNewspaper > 0:
			paperCounts.append([newspaper, numberResultsForNewspaper, newspaperCode])
		return paperCounts

	def makeChunkedDictionary(self, chunkSize):
		listOfSubDicts = []
		initialList = []
		for paper in self.newspaperDictionary:
			initialList.append(paper)
		currentIndex = 0
		for i in range(ceil((len(self.newspaperDictionary) / chunkSize)) - 1):
			subDict = {}
			subList = initialList[currentIndex:currentIndex+chunkSize]
			currentIndex = currentIndex + chunkSize
			for paper in subList:
				subDict[paper] = self.newspaperDictionary[paper]
			listOfSubDicts.append(subDict)
		subDict = {}
		subList = initialList[currentIndex:]
		for paper in subList:
			subDict[paper] = self.newspaperDictionary[paper]
		listOfSubDicts.append(subDict)
		self.chunkedNewspaperDictionary = listOfSubDicts

#Needs some work, likely broken in some way, haven't looked at it in a while.
class FullSearchNoDictionary(GallicaSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, progressTracker):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange, progressTracker)

	def runSearch(self):
		iterations = ceil(self.totalResults / 50)
		startRecordList = []
		for i in range(iterations):
			startRecordList.append((i * 50) + 1)
		with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
			for i, result in enumerate(executor.map(self.sendWorkersToSearch, startRecordList), 1):
				self.updateRetrievalProgressPercent(i, iterations)
				self.collectedQueries.extend(result)
		self.updateRetrievalProgressPercent(100, 100)
		self.packageQuery()

	def sendWorkersToSearch(self, startRecord):
		batchHunter = self.sendQuery(self.baseQuery, startRecord=startRecord, numRecords=50)
		results = batchHunter.getResultList()
		return results

	def findTotalResults(self):
		hunterForTotalNumberOfQueryResults = GallicaSearch.sendQuery(self.baseQuery, numRecords=1, startRecord=1)
		self.totalResults = hunterForTotalNumberOfQueryResults.establishTotalHits(self.baseQuery, False)


# make list of newspapers with number results. Do at the end of all queries (since # results updated during lower level runs)


DEFAULT_TIMEOUT = 1  # seconds


class TimeoutAndRetryHTTPAdapter(HTTPAdapter):
	def __init__(self, *args, **kwargs):
		retryStrategy = Retry(
			total=10,
			status_forcelist=[500, 502, 503, 504],
			method_whitelist=["HEAD", "GET", "OPTIONS", "PUT", "DELETE"],
			backoff_factor=1
		)
		self.timeout = DEFAULT_TIMEOUT
		if "timeout" in kwargs:
			self.timeout = kwargs["timeout"]
			del kwargs["timeout"]
		super().__init__(*args, **kwargs, max_retries=retryStrategy)

	def send(self, request, **kwargs):
		timeout = kwargs.get("timeout")
		if timeout is None:
			kwargs["timeout"] = self.timeout
		return super().send(request, **kwargs)
