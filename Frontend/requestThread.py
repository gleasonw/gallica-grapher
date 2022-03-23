import re
import threading
from requests import ReadTimeout
from Backend.GettingAndGraphing.mainSearchSupervisor import MainSearchSupervisor
import uuid
import psycopg2


class RequestThread(threading.Thread):
	def __init__(self, searchTerm, papers, yearRange, strictness, requestID):
		splitter = re.compile("[\w']+")
		self.searchItems = re.findall(splitter, searchTerm)
		self.paperChoices = papers
		self.cleanPaperChoices()
		self.yearRange = re.findall(splitter, yearRange)
		self.strictness = strictness
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
		requestToRun = MainSearchSupervisor(self.searchItems, self.paperChoices, self.yearRange, self.strictness,
											self, graphType="bar",
											uniqueGraphs=False, samePage=True)
		try:
			requestToRun.runMultiTermQuery()
		except ReadTimeout:
			print("Egads!")

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

	def getDateRange(self):
		return self.yearRange

	def getRequestID(self):
		return self.id

	def setTopPapers(self, papers):
		self.listOfTopPapersForTerms = papers

	def getTopPapers(self):
		return self.listOfTopPapersForTerms

	def getGraphingStatus(self):
		return self.graphingFinishedStatus

	def setGraphingStatus(self, finishedStatus):
		self.graphingFinishedStatus = finishedStatus



if __name__ == "__main__":
	request = RequestThread("algérie", [], "1800-1900",False,str(uuid.uuid4()))
	request.run()
	try:
		conn = psycopg2.connect(
			host="localhost",
			database="postgres",
			user="wglea",
			password="ilike2play"
		)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM results;")
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		raise
	finally:
		if conn is not None:
			conn.close()