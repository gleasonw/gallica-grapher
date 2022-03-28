import psycopg2
import os
import concurrent.futures
from math import ceil

from requests_toolbelt import sessions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from Backend.GettingAndGraphing.batchGetter import BatchGetter
from Backend.GettingAndGraphing.dictionaryMaker import DictionaryMaker

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


class TermSearch:

	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, progressTrackerThread, **kwargs):
		self.lowYear = None
		self.highYear = None
		self.isYearRange = None
		self.baseQuery = None
		self.progressTrackerThread = progressTrackerThread
		self.requestID = progressTrackerThread.getRequestID()
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
		self.listOfAllRequestStrings = []

		self.paperNameCounts = []

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

	@staticmethod
	def sendQuery(queryToSend, **kwargs):
		session = TermSearch.makeSession()
		if kwargs['startRecord'] is None:
			startRecord = 1
		else:
			startRecord = kwargs['startRecord']
		if kwargs['numRecords'] is None:
			numRecords = 50
		else:
			numRecords = kwargs['numRecords']
		hunter = BatchGetter(queryToSend, startRecord, numRecords, session)
		hunter.hunt()
		return hunter

	def packageQuery(self):
		if len(self.collectedQueries) != 0:
			self.postResultsToDB()
		else:
			pass

	def postResultsToDB(self):
			conn = None
			try:
				conn = psycopg2.connect(
					host="localhost",
					database="postgres",
					user="wglea",
					password="ilike2play"
				)
				cursor = conn.cursor()
				for entry in self.collectedQueries:
					entryDateBits = entry.get('date').split('-')
					entryMonth = entryDateBits[1]
					entryYear = entryDateBits[0]
					entryDay = entryDateBits[2]
					cursor.execute("""
					INSERT INTO results (identifier, day, month, year, searchterm, paperID, requestid)
					VALUES (%s, %s, %s, %s, %s, %s, %s);
					""",
					(entry.get('identifier'), entryDay, entryMonth, entryYear, self.searchTerm, entry.get('code'), self.requestID))
					conn.commit()
				for i in range(len(self.topTenPapers)):
					paperPosition = i + 1
					paperNameCount = self.topTenPapers[i]
					paperName = paperNameCount[0]
					paperCount = paperNameCount[1]
					cursor.execute("""
										INSERT INTO toppapers (papername, position, requestid, count)
										VALUES (%s, %s, %s, %s);
										""",
								   (paperName, paperPosition, self.requestID, paperCount))
					conn.commit()

			except (Exception, psycopg2.DatabaseError) as error:
				print(error)
			finally:
				if conn is not None:
					conn.close()

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
			if not self.newspaperDictionary:
				self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and (gallica adj "{' \
								 '{searchWord}}") sortby dc.date/sort.ascending '
			else:
				self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and ((arkPress all "{{{{' \
								 'newsKey}}}}") and (gallica adj "{{searchWord}}")) sortby dc.date/sort.ascending '
			self.baseQuery = self.baseQuery.format(firstYear=str(self.lowYear), secondYear=str(self.highYear))
		else:
			if not self.newspaperDictionary:
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

	#Might be a little slow, why do I do this again?
	def updateNewspaperCountDictionary(self):
		currentCount = 0
		for paperName, paperCode in self.newspaperDictionary.items():
			for result in self.collectedQueries:
				resultPaperCode = result.get("code")
				if paperCode == resultPaperCode:
					currentCount += 1
			self.updateTopTenPapers(paperName, currentCount)
			self.numResultsForEachPaper.update({paperName: currentCount})
			currentCount = 0
		pass

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


class FullSearchWithinDictionary(TermSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, progressTracker):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange, progressTracker)

	def runSearch(self):
		self.findTotalResults()
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
			startRecord = 1
			for i in range(numberOfQueriesToSend):
				recordAndCode = [startRecord, newspaperKey]
				self.listOfAllRequestStrings.append(recordAndCode)
				startRecord += 50

	def createWorkersForSearch(self):
		progress = 0
		with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
			for result in executor.map(self.sendWorkersToSearch, self.listOfAllRequestStrings):
				numberResultsInBatch = len(result)
				self.collectedQueries.extend(result)
				progress = progress + numberResultsInBatch
				self.updateRetrievalProgressPercent(progress, self.totalResults)
			self.updateRetrievalProgressPercent(100, 100)

	#TODO: speed up querying by batching more queries into each worker's session?
	def sendWorkersToSearch(self, recordStartAndCode):
		recordStart = recordStartAndCode[0]
		code = recordStartAndCode[1]
		session = TermSearch.makeSession()
		queryFormatForPaper = self.baseQuery.format(newsKey=code)
		hunterForQuery = BatchGetter(queryFormatForPaper, recordStart, 50, session)
		hunterForQuery.hunt()
		results = hunterForQuery.getResultList()
		for result in results:
			result["code"] = code
		return results

	def findTotalResults(self):
		self.createWorkersForFindingTotalResults()
		self.progressTrackerThread.setNumberDiscoveredResults(self.totalResults)

	def createWorkersForFindingTotalResults(self):
		try:
			with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
				for i, result in enumerate(executor.map(self.findNumberResults, self.newspaperDictionary), 1):
					if result:
						self.paperNameCounts = self.paperNameCounts + result
					self.updateDiscoveryProgressPercent(i, len(self.newspaperDictionary))
			self.generateNewspaperDictionary()
		except Exception as error:
			print(error)
			raise

	def findNumberResults(self, newspaper):
		session = TermSearch.makeSession()
		paperCounts = []
		newspaperCode = self.newspaperDictionary[newspaper]
		newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
		hunterForTotalNumberOfQueryResults = BatchGetter(newspaperQuery, 1, 1, session)
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
class FullSearchNoDictionary(TermSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, progressTracker):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange, progressTracker)

	def runSearch(self):
		self.findTotalResults()
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
		hunterForTotalNumberOfQueryResults = TermSearch.sendQuery(self.baseQuery, numRecords=1, startRecord=1)
		self.totalResults = hunterForTotalNumberOfQueryResults.establishTotalHits(self.baseQuery, False)


# make list of newspapers with number results. Do at the end of all queries (since # results updated during lower level runs)


DEFAULT_TIMEOUT = 10  # seconds


class TimeoutAndRetryHTTPAdapter(HTTPAdapter):
	def __init__(self, *args, **kwargs):
		retryStrategy = Retry(
			total=15,
			status_forcelist=[500, 502, 503, 504],
			method_whitelist=["HEAD", "GET", "OPTIONS", "PUT", "DELETE"],
			backoff_factor=2
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
