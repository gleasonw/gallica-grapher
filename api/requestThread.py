import re
import threading
from Backend.GettingAndGraphing.supervisorOfResultGetters import SupervisorOfResultGetters
import uuid


class RequestThread(threading.Thread):
	def __init__(self, searchTerms, papers, yearRange, requestID, eliminateEdgePapers=False, paperTrendLines=False, termTrendLines=False):
		splitter = re.compile("[\w']+")
		self.searchItems = searchTerms
		self.paperChoices = papers
		self.cleanPaperChoices()
		self.yearRange = re.findall(splitter, yearRange)
		self.tolerateEdgePapers = eliminateEdgePapers
		self.paperTrendLines = paperTrendLines
		self.termTrendLines = termTrendLines
		self.discoveryProgress = 0
		self.retrievalProgress = 0
		self.currentTerm = ""
		self.graphJSON = None
		self.totalResultsForQuery = 0
		self.numberRetrievedResults = 0
		self.listOfTopPapersForTerms = []
		self.id = requestID
		self.graphingFinishedStatus = False
		super().__init__()

	def run(self):
		requestToRun = SupervisorOfResultGetters(self.searchItems, self.paperChoices, self.yearRange, self.tolerateEdgePapers, self.paperTrendLines,
												 self.termTrendLines,
												 self)
		requestToRun.generateTermRetrievalObjects()
		requestToRun.retrieveResults()
		requestToRun.closeDbConnectionForRequest()

	def cleanPaperChoices(self):
		for i, paper in enumerate(self.paperChoices):
			paper = self.paperChoices[i]
			self.paperChoices[i] = paper.strip()

	def setRetrievalProgress(self, amount):
		self.retrievalProgress = amount

	def setDiscoveryProgress(self, amount):
		self.discoveryProgress = amount

	def setCurrentTerm(self, term):
		self.currentTerm = term

	def getCurrentTerm(self):
		return self.currentTerm

	def getRetrievalProgress(self):
		return self.retrievalProgress

	def getDiscoveryProgress(self):
		return self.discoveryProgress

	def setNumberDiscoveredResults(self, total):
		self.totalResultsForQuery = total

	def getNumberDiscoveredResults(self):
		return self.totalResultsForQuery

	def setNumberRetrievedResults(self, count):
		self.numberRetrievedResults = count

	def getNumberRetrievedResults(self):
		return self.numberRetrievedResults

	def getSearchItems(self):
		return self.searchItems

	def getDateRangeString(self):
		return f"{self.yearRange[0]} to {self.yearRange[1]}"

	def getRequestID(self):
		return self.id

	def setTopPapers(self, papers):
		self.listOfTopPapersForTerms = papers

	def getTopPapers(self):
		return self.listOfTopPapersForTerms

	def getGraphingStatus(self):
		return self.graphingFinishedStatus

	def setGraphJSON(self, json):
		self.graphJSON = json

	def getGraphJSON(self):
		return self.graphJSON

	def setGraphingStatus(self, finishedStatus):
		self.graphingFinishedStatus = finishedStatus



if __name__ == "__main__":
	request = RequestThread(["brazza","malamine"],
							[],
							"1850-1950",
							str(uuid.uuid4()),
							eliminateEdgePapers=False)
	request.run()