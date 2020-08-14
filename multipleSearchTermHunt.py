from huntOverseer import HuntOverseer


# Different papers for each term? Oohhhh... only unlimited. Thank you.
class MultipleSearchTermHunt:
	def __int__(self, searchList, newspaper, yearRange, strictYearRange, **kwargs):
		self.searchTermList = searchList
		self.newspaper = newspaper
		self.yearRange = yearRange
		self.strictYearRange = strictYearRange
		self.searchTermResultList = []
		self.theKwargsForGraphingAndRecordNumber = kwargs

	def runMultiTermQuery(self):
		for searchTerm in self.searchTermList:
			resultGetterForTerm = HuntOverseer(searchTerm, self.newspaper, self.yearRange, self.strictYearRange,
											   self.theKwargsForGraphingAndRecordNumber["recordNumber"])
			self.searchTermResultList.append(resultGetterForTerm)
		self.putTheResultsInFiles(self)

	def putTheResultsInFiles(self):
		for resultBundle in self.searchTermResultList:
			resultBundle.packageQuery()

	def initiateGraphing(self):
		for resultBundle in self.searchTermList:
			fileName = resultBundle.getFileName()
			topTenPapers = resultBundle.getTopTenPapers()
			grapher = GallicaGrapher(fileName, topTenPapers, self.theKwargsForGraphingAndRecordNumber)



	def runMultiTermQueryWithDiffPapers(self):
		pass
