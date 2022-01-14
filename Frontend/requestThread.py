import re
import threading
from requests import ReadTimeout
from Backend.GettingAndGraphing.mainSearchSupervisor import MultipleSearchTermHunt


class RequestThread(threading.Thread):
	def __init__(self, searchTerm, papers, yearRange, strictness):
		splitter = re.compile("[\w']+")
		self.searchItems = re.findall(splitter, searchTerm)
		self.paperChoices = papers
		self.cleanPaperChoices()
		self.yearRange = re.findall(splitter, yearRange)
		self.strictness = strictness
		self.discoveryProgress = 0
		self.retrievalProgress = 0
		self.currentTerm = ""
		self.threadId = id
		self.imageRef = None
		self.totalResultsForQuery = 0
		self.numberRetrievedResults = 0
		self.listOfTopPapersForTerms = []

		super().__init__()

	def run(self):
		requestToRun = MultipleSearchTermHunt(self.searchItems, self.paperChoices, self.yearRange, self.strictness,
											  self, graphType="bar",
											  uniqueGraphs=False, samePage=True)
		try:
			requestToRun.runMultiTermQuery()
		except ReadTimeout:
			pass

	def cleanPaperChoices(self):
		for i in range(len(self.paperChoices)):
			paper = self.paperChoices[i]
			self.paperChoices[i] = paper.strip()

	def setRetrievalProgress(self, amount):
		self.retrievalProgress = amount

	def setDiscoveryProgress(self, amount):
		self.discoveryProgress = amount

	def getRetrievalProgress(self):
		return self.retrievalProgress

	def getDiscoveryProgress(self):
		return self.discoveryProgress

	def getId(self):
		return self.threadId

	def setImageRef(self, ref):
		self.imageRef = ref

	def getImageRef(self):
		return self.imageRef

	def setDiscoveredResults(self, total):
		self.totalResultsForQuery = total

	def getDiscoveredResults(self):
		return self.totalResultsForQuery

	def setNumberRetrievedResults(self, count):
		self.numberRetrievedResults = count

	def getNumberRetrievedResults(self):
		return self.numberRetrievedResults

	def getSearchItems(self):
		return self.searchItems

	def getDateRange(self):
		return self.yearRange

	def addTopPapers(self, papers):
		self.listOfTopPapersForTerms.append(papers)

	def getTopPapers(self):
		return self.listOfTopPapersForTerms
