from typing import List, Any

from gallicaHunter import GallicaHunter
from math import ceil
from multiprocessing import Pool, Manager, Lock


class OverseerOfNewspaperHunt():
	allResults: List[Any]

	def __init__(self, query, numberResults):
		self.currentProcessedResults = 0
		self.startRecordForGallicaQuery = 1
		self.currentNumValidResults = 0
		self.query = query
		self.numberResults = numberResults
		self.allResults = Manager().list()
		self.currentAndProcessedLock = Lock()

	def scourPaper(self):
		pass

	def getResultList(self):
		return self.allResults[0]

	def getNumberValidResults(self):
		return self.currentNumValidResults

	def resultCounter(self, queryGetObject):
		numPurgedResults = queryGetObject.getNumberPurgedResults()
		queryResults = queryGetObject.getResultList()
		self.iterateProcessedAndValid(len(queryResults), numPurgedResults)

	def iterateProcessedAndValid(self, numRetrieved, numPurged):
		self.currentAndProcessedLock.acquire()
		self.currentProcessedResults = self.currentProcessedResults + numRetrieved + numPurged
		self.currentNumValidResults = self.currentProcessedResults - numPurged
		self.currentAndProcessedLock.release()

	@staticmethod
	def sendQuery(queryToSend, startRecord, numRecords):
		hunter = GallicaHunter(queryToSend, startRecord, numRecords)
		hunter.hunt()
		return hunter


class LimitedOverseerOfNewspaperHunt(OverseerOfNewspaperHunt):
	def __init__(self, query, numberResults, maxResults):
		super().__init__(query, numberResults)
		self.maxResults = maxResults

	def scourPaper(self):

		while self.maxResults > self.currentProcessedResults:
			amountRemaining = self.maxResults - self.currentProcessedResults
			if amountRemaining >= 50:
				numRecords = 50
			else:
				numRecords = amountRemaining
			batchHunter = OverseerOfNewspaperHunt.sendQuery(self.query, self.startRecordForGallicaQuery, numRecords)
			self.resultCounter(batchHunter)


class UnlimitedOverseerOfNewspaperHunt(OverseerOfNewspaperHunt):
	def __init__(self, query, numberResults):
		super().__init__(query, numberResults)

	def scourPaper(self):
		numberQueriesToSend = ceil(self.numberResults / 50)
		with Pool(10) as pool:
			self.allResults.append(pool.map(self.createGallicaHunters, range(numberQueriesToSend)))

	def createGallicaHunters(self, iterationNumber):
		startRecord = iterationNumber * 50
		startRecord = startRecord + 1
		batchHunter = OverseerOfNewspaperHunt.sendQuery(self.query, startRecord, 50)
		self.resultCounter(batchHunter)
		return batchHunter.getResultList()
