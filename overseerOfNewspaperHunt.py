from typing import List, Any

from gallicaHunter import GallicaHunter


class OverseerOfNewspaperHunt():
	allResults: List[Any]

	def __init__(self, query, numberResults):
		self.currentProcessedResults = 0
		self.startRecordForGallicaQuery = 1
		self.currentNumValidResults = 0
		self.query = query
		self.numberResults = numberResults
		self.allResults = []

	def scourPaper(self):
		pass

	def getResultList(self):
		return self.allResults

	def getNumberValidResults(self):
		return self.currentNumValidResults

	def resultGetterCounter(self, queryGetObject):
		numPurgedResults = queryGetObject.getNumberPurgedResults()
		queryResults = queryGetObject.getResultList()
		self.allResults = self.allResults + queryResults
		self.currentProcessedResults = self.currentProcessedResults + len(queryResults) + numPurgedResults
		self.currentNumValidResults = self.currentProcessedResults - numPurgedResults
		self.startRecordForGallicaQuery = self.startRecordForGallicaQuery + 50

	@staticmethod
	def sendQuery(queryToSend, startRecord, numRecords):
		hunter = GallicaHunter(queryToSend, startRecord, numRecords)
		hunter.hunt()
		return hunter
