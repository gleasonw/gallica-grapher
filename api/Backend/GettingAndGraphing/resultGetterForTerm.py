import datetime, os, psycopg2
from requests import ReadTimeout
from math import ceil
from concurrent.futures.thread import ThreadPoolExecutor

from requests_toolbelt import sessions
from time import perf_counter

from timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from batchGetter import BatchGetter
from dictionaryMaker import DictionaryMaker
from paperGetterFromGallica import PaperGetterFromGallica

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


class ResultGetterForTerm:

	def __init__(self, searchTerm, yearRange, progressTrackerThread, dbConnection, newspaperList=None, strictYearRange=False):
		self.lowYear = None
		self.highYear = None
		self.isYearRange = None
		self.baseQuery = None
		self.progressTrackerThread = progressTrackerThread
		self.requestID = progressTrackerThread.getRequestID()
		self.eliminateEdgePapers = strictYearRange
		self.establishStrictness()
		self.totalResults = 0
		self.discoveryProgressPercent = 0
		self.retrievalProgressPercent = 0
		self.progressIterations = 0
		self.newspaperList = newspaperList
		self.newspaperDictionary = {}
		self.collectedQueries = []
		self.searchTerm = searchTerm
		self.topTenPapers = None
		self.numResultsForEachPaper = {}
		self.establishYearRange(yearRange)
		self.buildQuery()
		self.listOfAllRequestStrings = []
		self.currentEntryDataJustInCase = None
		self.dbConnection = dbConnection
		self.paperNameCounts = []
		self.gallicaHttpSession = ResultGetterForTerm.makeSession()

	def getTopTenPapers(self):
		return self.topTenPapers

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
		adapter = TimeoutAndRetryHTTPAdapter(timeout=25)
		gallicaHttpSession.mount("https://", adapter)
		gallicaHttpSession.mount("http://", adapter)
		return gallicaHttpSession

	def discoverTopTenPapers(self):
		try:
			cursor = self.dbConnection.cursor()
			cursor.execute("""
				SELECT count(requestResults.identifier) AS papercount, papers.papername
					FROM (SELECT identifier, paperid FROM results WHERE requestid = %s AND searchterm = %s) AS requestResults 
					INNER JOIN papers ON requestResults.paperid = papers.papercode 
					GROUP BY papers.papername 
					ORDER BY papercount DESC
					LIMIT 10;
			""", (self.requestID, self.searchTerm))
			self.topTenPapers = cursor.fetchall()
			pass
		except psycopg2.DatabaseError as error:
			print(error)

	def postResultsToDB(self):
		print("Num collected: ", len(self.collectedQueries))
		try:
			for hitList in self.collectedQueries:
				self.currentEntryDataJustInCase = hitList
				self.insertOneResultToTable(hitList)
		except psycopg2.IntegrityError as e:
			try:
				print(e)
				missingCode = self.currentEntryDataJustInCase.get('journalCode')
				paperFetcher = PaperGetterFromGallica(self.dbConnection)
				paperFetcher.addPaperToDBbyCode(missingCode)
				self.insertOneResultToTable(self.currentEntryDataJustInCase)
			except psycopg2.DatabaseError:
				raise

	def insertOneResultToTable(self, entry):
		cursor = self.dbConnection.cursor()
		entryDateBits = entry.get('date').split('-')
		entryMonth = int(entryDateBits[1])
		entryYear = int(entryDateBits[0])
		entryDay = int(entryDateBits[2])
		entryDate = datetime.datetime(entryYear, entryMonth, entryDay)
		cursor.execute("""
						INSERT INTO results (identifier, date, searchterm, paperID, requestid)
						VALUES (%s, %s, %s, %s, %s);
						""",
					   (entry.get('identifier'), entryDate, self.searchTerm,
						entry.get('journalCode'), self.requestID))

	def establishStrictness(self):
		if self.eliminateEdgePapers in ["ya", "True", "true", "yes", "absolutely"]:
			self.eliminateEdgePapers = True
		else:
			self.eliminateEdgePapers = False

	def parseNewspaperDictionary(self):
		dicParser = DictionaryMaker(self.newspaperList, self.dbConnection)
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
			if not self.newspaperList:
				self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and (gallica adj "{' \
								 '{searchWord}}") and (dc.type all "fascicule") sortby dc.date/sort.ascending '
			else:
				self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and ((arkPress all "{{{{' \
								 'newsKey}}}}_date") and (gallica adj "{{searchWord}}")) sortby dc.date/sort.ascending '
			self.baseQuery = self.baseQuery.format(firstYear=str(self.lowYear), secondYear=str(self.highYear))
		else:
			if not self.newspaperList:
				self.baseQuery = '(gallica adj "{searchWord}") and (dc.type all "fascicule") sortby dc.date/sort.ascending'
			else:
				self.baseQuery = 'arkPress all "{{newsKey}}_date" and (gallica adj "{searchWord}") sortby dc.date/sort.ascending'
		self.baseQuery = self.baseQuery.format(searchWord=self.searchTerm)
		pass

	def runSearch(self):
		pass

	def completeSearch(self):
		self.updateRetrievalProgressPercent(100, 100)
		if len(self.collectedQueries) != 0:
			self.postResultsToDB()
			self.discoverTopTenPapers()

	def findTotalResults(self):
		pass

	def updateDiscoveryProgressPercent(self, iteration, total):
		self.discoveryProgressPercent = int((iteration / total) * 100)
		self.progressTrackerThread.setDiscoveryProgress(self.discoveryProgressPercent)

	def updateRetrievalProgressPercent(self, iteration, total):
		self.retrievalProgressPercent = int((iteration / total) * 100)
		self.progressTrackerThread.setRetrievalProgress(self.retrievalProgressPercent)


class ResultGetterForTermSelectPapers(ResultGetterForTerm):
	def __init__(self, searchTerm, newspaperList, yearRange, progressTracker, dbConnection):
		super().__init__(searchTerm, yearRange, progressTracker, dbConnection, newspaperList=newspaperList)

	def runSearch(self):
		self.parseNewspaperDictionary()
		self.findTotalResults()
		self.createQueryStringList()
		self.executeSearch()
		self.progressTrackerThread.setNumberRetrievedResults(len(self.collectedQueries))
		self.completeSearch()

	def createQueryStringList(self):
		for newspaper in self.newspaperDictionary:
			hitsInNewspaper = self.numResultsForEachPaper[newspaper]
			newspaperKey = self.newspaperDictionary[newspaper]
			numberOfQueriesToSend = ceil(hitsInNewspaper / 50)
			startRecord = 1
			for i in range(numberOfQueriesToSend):
				recordAndCode = [startRecord, newspaperKey]
				self.listOfAllRequestStrings.append(recordAndCode)
				startRecord += 50

	def executeSearch(self):
		progress = 0
		with ThreadPoolExecutor(max_workers=150) as executor:
			for result in executor.map(self.sendWorkersToSearch, self.listOfAllRequestStrings):
				numberResultsInBatch = len(result)
				self.collectedQueries.extend(result)
				progress = progress + numberResultsInBatch
				self.updateRetrievalProgressPercent(progress, self.totalResults)

	# TODO: speed up querying by batching more queries into each worker's session?
	def sendWorkersToSearch(self, recordStartAndCode):
		recordStart = recordStartAndCode[0]
		code = recordStartAndCode[1]
		queryFormatForPaper = self.baseQuery.format(newsKey=code)
		hunterForQuery = BatchGetter(queryFormatForPaper, recordStart, 50, self.gallicaHttpSession)
		try:
			hunterForQuery.hunt()
		except ReadTimeout:
			print("Failed request!")
		results = hunterForQuery.getResultList()
		return results

	def findTotalResults(self):
		self.createWorkersForFindingTotalResults()
		self.generateNewspaperNumResultsDictionary()
		self.sumUpNewspaperResultsForTotalResults()
		self.progressTrackerThread.setNumberDiscoveredResults(self.totalResults)

	def createWorkersForFindingTotalResults(self):
		try:
			with ThreadPoolExecutor(max_workers=50) as executor:
				for i, result in enumerate(executor.map(self.findNumberResultsForOneNewspaper, self.newspaperDictionary), 1):
					if result:
						self.paperNameCounts = self.paperNameCounts + result
					self.updateDiscoveryProgressPercent(i, len(self.newspaperDictionary))
		except Exception as error:
			print(error)
			raise

	def findNumberResultsForOneNewspaper(self, newspaper):
		paperCounts = []
		newspaperCode = self.newspaperDictionary[newspaper]
		newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
		hunterForTotalNumberOfQueryResults = BatchGetter(newspaperQuery, 1, 1, self.gallicaHttpSession)
		numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
		if numberResultsForNewspaper > 0:
			paperCounts.append([newspaper, numberResultsForNewspaper, newspaperCode])
		return paperCounts

	def generateNewspaperNumResultsDictionary(self):
		self.newspaperDictionary.clear()
		for nameCountCode in self.paperNameCounts:
			paperName = nameCountCode[0]
			paperCount = nameCountCode[1]
			paperCode = nameCountCode[2]
			self.newspaperDictionary.update({paperName: paperCode})
			self.numResultsForEachPaper.update({paperName: paperCount})

	def sumUpNewspaperResultsForTotalResults(self):
		for paper in self.numResultsForEachPaper:
			self.totalResults += self.numResultsForEachPaper[paper]


class ResultGetterForTermAllPapers(ResultGetterForTerm):
	def __init__(self, searchTerm, yearRange, eliminateEdgePapers, progressTracker, dbConnection):
		super().__init__(searchTerm, yearRange, progressTracker, dbConnection, strictYearRange=eliminateEdgePapers)

	def runSearch(self):
		self.findTotalResults()
		self.updateDiscoveryProgressPercent(100, 100)
		iterations = ceil(self.totalResults / 50)
		startRecordList = [(i * 50) + 1 for i in range(iterations)]
		start = perf_counter()
		with ThreadPoolExecutor(max_workers=50) as executor:
			for i, result in enumerate(executor.map(self.sendWorkersToSearch, startRecordList)):
				self.updateRetrievalProgressPercent(i, iterations)
				self.collectedQueries.extend(result)
		end = perf_counter()
		print(f'Total request time: {end - start}')
		if self.eliminateEdgePapers:
			self.cullResultsFromEdgePapers()
		self.completeSearch()

	def sendWorkersToSearch(self, startRecord):
		hunter = BatchGetter(self.baseQuery, startRecord, 50, self.gallicaHttpSession)
		try:
			hunter.hunt()
		except ReadTimeout:
			print("Failed request!")
		results = hunter.getResultList()
		return results

	#TODO: This syntax is confusing
	def findTotalResults(self):
		hunter = BatchGetter(self.baseQuery, 1, 1, self.gallicaHttpSession)
		self.totalResults = hunter.establishTotalHits(self.baseQuery, False)
		self.progressTrackerThread.setNumberDiscoveredResults(self.totalResults)

	def cullResultsFromEdgePapers(self):
		try:
			cursor = self.dbConnection.cursor()
			startYear = datetime.date(int(self.lowYear), 1, 1)
			endYear = datetime.date(int(self.highYear), 1, 1)
			cursor.execute("""
			DELETE FROM results 
				WHERE results.requestID = %s 
				AND
				results.paperID IN (SELECT papercode FROM papers WHERE (papers.startyear > %s AND papers.startyear < %s) OR (papers.endyear < %s AND papers.endyear > %s));
			""", (self.requestID, startYear, endYear, endYear, startYear))
		except psycopg2.DatabaseError as e:
			print(e)



