from overseerOfNewspaperHunt import OverseerOfNewspaperHunt

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
			self.resultGetterCounter(batchHunter)





