from overseerOfNewspaperHunt import OverseerOfNewspaperHunt


class UnlimitedOverseerOfNewspaperHunt(OverseerOfNewspaperHunt):
	def __init__(self, query, numberResults):
		super().__init__(query, numberResults)

	def scourPaper(self):
		while self.numberResults > self.currentProcessedResults:
			batchHunter = OverseerOfNewspaperHunt.sendQuery(self.query, self.startRecordForGallicaQuery, 50)
			numPurgedResults = batchHunter.getNumberPurgedResults()
			self.results = batchHunter.getResultList()
			self.currentProcessedResults = self.currentProcessedResults + len(
				self.results) + numPurgedResults
			self.currentNumValidResults = self.currentProcessedResults - numPurgedResults
			self.startRecordForGallicaQuery = self.startRecordForGallicaQuery + 50
