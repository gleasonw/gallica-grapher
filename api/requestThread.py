import re
import threading
from Backend.GettingAndGraphing.ticketQuery import TicketQuery

#for testing
import uuid


class RequestThread(threading.Thread):
	def __init__(self, searchTerms, papers, yearRange, requestID, eliminateEdgePapers=False):
		splitter = re.compile("[\w']+")
		self.searchItems = searchTerms
		self.paperChoices = papers
		self.yearRange = re.findall(splitter, yearRange)
		self.tolerateEdgePapers = eliminateEdgePapers
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
		requestToRun = TicketQuery(
				self.searchItems,
				self.paperChoices,
				self.yearRange,
				self.tolerateEdgePapers,
				self)
		requestToRun.start()

	def setProgress(self, amount):
		self.discoveryProgress = amount

	def getProgress(self):
		return self.discoveryProgress

	def setCurrentTerm(self, term):
		self.currentTerm = term

	def getCurrentTerm(self):
		return self.currentTerm

	def setNumberDiscoveredResults(self, total):
		self.totalResultsForQuery = total

	def getNumberDiscoveredResults(self):
		return self.totalResultsForQuery

	def setNumberRetrievedResults(self, count):
		self.numberRetrievedResults = count

	def getNumberRetrievedResults(self):
		return self.numberRetrievedResults

	def getRequestID(self):
		return self.id

	def setTopPapers(self, papers):
		self.listOfTopPapersForTerms = papers

	def getTopPapers(self):
		return self.listOfTopPapersForTerms

	def setGraphJSON(self, json):
		self.graphJSON = json

	def getGraphJSON(self):
		return self.graphJSON

if __name__ == "__main__":
	request = RequestThread(["brazza","malamine"],
							[],
							"1850-1950",
							str(uuid.uuid4()),
							eliminateEdgePapers=False)
	request.run()