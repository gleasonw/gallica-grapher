from overseerOfNewspaperHunt import OverseerOfNewspaperHunt


class UnlimitedOverseerOfNewspaperHunt(OverseerOfNewspaperHunt):
	def __init__(self, query, numberResults):
		super().__init__(query, numberResults)

	def scourPaper(self):
		while self.numberResults > self.currentProcessedResults:
			batchHunter = OverseerOfNewspaperHunt.sendQuery(self.query, self.startRecordForGallicaQuery, 50)
			self.resultGetterCounter(batchHunter)
