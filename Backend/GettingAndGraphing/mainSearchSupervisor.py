

from Backend.GettingAndGraphing.termSearch import *
from Backend.GettingAndGraphing.grapher import Grapher

import time


class MainSearchSupervisor:

	def __init__(self, searchList, newspaper, yearRange, strictYearRange, progressTrackerThread, **kwargs):
		self.searchTermList = searchList
		self.newspaper = newspaper
		self.yearRange = yearRange
		self.strictYearRange = strictYearRange
		self.searchTermResultList = []
		self.theKwargsForGraphingAndRecordNumber = kwargs
		self.listOfGraphers = []
		self.bigFileName = ''
		self.progressTrackerThread = progressTrackerThread
		self.requestID = progressTrackerThread.getRequestID()

	def getAllResultBundlers(self):
		return self.searchTermResultList

	def runMultiTermQuery(self):
		for searchTerm in self.searchTermList:
			#TODO: Fix the full search
			resultGetterForTerm = FullSearchWithinDictionary(searchTerm, self.newspaper,
															 self.yearRange,
															 self.strictYearRange, self.progressTrackerThread)
			self.searchTermResultList.append(resultGetterForTerm)
			start = time.time()
			resultGetterForTerm.runSearch()
			print("Elapsed query time: {0}".format(time.time() - start))
		start = time.time()
		self.initiateGraphing()
		print("Elapsed graphing time: {0}".format(time.time()-start))
		#TODO: Change to accomodate top ten papers if multiple search terms. Very temporary solution.
		resultBundle = self.searchTermResultList[0]
		topPapers = resultBundle.getTopTenPapers()
		self.progressTrackerThread.setTopPapers(topPapers)

	def initiateGraphing(self):
		if self.theKwargsForGraphingAndRecordNumber['uniqueGraphs']:
			if self.theKwargsForGraphingAndRecordNumber['samePage']:
				#Single page many graphs?
				pass
			else:
				#Many pages of graphs?
				pass
		else:
			self.initiateSingleGraphManyData()

	# What exactly does a top ten dictionary mean in this context of multiple terms?
	def initiateSingleGraphManyData(self):
		grapher = Grapher(self.theKwargsForGraphingAndRecordNumber, self.requestID)
		grapher.graph()
		self.progressTrackerThread.setGraphingStatus(True)

	def runMultiTermQueryWithDiffPapers(self):
		pass


