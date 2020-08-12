from gallicaHunter import GallicaHunter


class OverseerOfNewspaperHunt():
	def __init__(self, query, numberResults):
		self.currentProcessedResults = 0
		self.startRecordForGallicaQuery = 1
		self.currentNumValidResults = 0
		self.currentNumPurgedResults = None
		self.query = query
		self.numberResults = numberResults
		self.results = []

	def scourPaper(self):
		pass

	def getResultList(self):
		return self.results

	def getNumberValidResults(self):
		return self.currentNumValidResults

	@staticmethod
	def sendQuery(queryToSend, startRecord, numRecords):
		hunter = GallicaHunter(queryToSend, startRecord, numRecords)
		hunter.hunt()
		return hunter
