from gallicaHunter import GallicaHunter
from math import ceil
from multiprocessing import Pool, cpu_count


class OverseerOfNewspaperHunt:

	def __init__(self, query, numberResults):
		self.numPurgedResults = 0
		self.currentProcessedResults = 0
		self.startRecordForGallicaQuery = 1
		self.query = query
		self.numberResults = numberResults
		self.allResults = []
		self.queryList = []

	def scourPaper(self):
		pass

	def getResultList(self):
		return self.allResults

	@staticmethod
	def sendQuery(queryToSend, startRecord, numRecords):
		hunter = GallicaHunter(queryToSend, startRecord, numRecords)
		hunter.hunt()
		return hunter

	def getNumValidResults(self):
		return len(self.allResults)

	def getNumProcessedResults(self):
		return len(self.allResults) + self.numPurgedResults


class LimitedOverseerOfNewspaperHunt(OverseerOfNewspaperHunt):
	def __init__(self, query, numberResults, maxResults):
		super().__init__(query, numberResults)
		self.maxResults = maxResults

	# Something is wrong here...
	def scourPaper(self):

		while self.maxResults > self.currentProcessedResults:
			amountRemaining = self.maxResults - self.currentProcessedResults
			if amountRemaining >= 50:
				numRecords = 50
			else:
				numRecords = amountRemaining
			batchHunter = OverseerOfNewspaperHunt.sendQuery(self.query, self.startRecordForGallicaQuery, numRecords)


class UnlimitedOverseerOfNewspaperHunt(OverseerOfNewspaperHunt):
	def __init__(self, query, numberResults):
		super().__init__(query, numberResults)

	def scourPaper(self):
		numberQueriesToSend = ceil(self.numberResults / 50)
		for i in range(numberQueriesToSend):
			result = self.createGallicaHunters(i)
			queryResults = result[0]
			numPurged = result[1]
			self.numPurgedResults = self.numPurgedResults + numPurged
			self.allResults = self.allResults + queryResults

	# Based on some not-so-rigorous testing threading the requests themselves, rather than the papers, is slower.

	# numCpus = cpu_count()
	# processes = min(numCpus, numberQueriesToSend)
	# with Pool(processes) as pool:
	# 	chunkSize = ceil(numberQueriesToSend / processes)
	# 	for result in pool.imap(self.createGallicaHunters, range(numberQueriesToSend), chunksize=chunkSize):
	# 		queryResults = result[0]
	# 		numPurged = result[1]
	# 		self.numPurgedResults = self.numPurgedResults + numPurged
	# 		self.allResults = self.allResults + queryResults

	def createGallicaHunters(self, iterationNumber):
		startRecord = iterationNumber * 50
		startRecord = startRecord + 1
		batchHunter = OverseerOfNewspaperHunt.sendQuery(self.query, startRecord=startRecord, numRecords=50)
		return [batchHunter.getResultList(), batchHunter.getNumberPurgedResults()]
