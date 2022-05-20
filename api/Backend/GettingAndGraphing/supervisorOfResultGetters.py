from Backend.GettingAndGraphing.resultGetterForTerm import *
from Backend.GettingAndGraphing.graphJSONmaker import GraphJSONmaker

import psycopg2


class SupervisorOfResultGetters:

	@staticmethod
	def connectToDatabase():
		conn = psycopg2.connect(
			host="localhost",
			database="gallicagrapher",
			user="wgleason",
			password="ilike2play"
		)
		conn.set_session(autocommit=True)
		return conn

	def __init__(self, searchList, newspaperList, yearRange, eliminateEdgePapers, paperTrendLines, termTrendLines, progressTrackerThread):
		self.searchTermList = searchList
		self.newspaperList = newspaperList
		self.topPaperList = None
		self.yearRange = yearRange
		self.eliminateEdgePapers = eliminateEdgePapers
		self.paperTrendLines = paperTrendLines
		self.termTrendLines = termTrendLines
		self.retrievalObjectList = []
		self.progressTrackerThread = progressTrackerThread
		self.requestID = progressTrackerThread.getRequestID()
		self.connectionToDB = SupervisorOfResultGetters.connectToDatabase()

	def getAllResultBundlers(self):
		return self.retrievalObjectList

	def closeDbConnectionForRequest(self):
		self.connectionToDB.close()
		self.connectionToDB = None

	# //TODO: No multi-term functionality yet
	def generateTermRetrievalObjects(self):
		if self.newspaperList:
			self.generateSelectPaperTermRetrievalObject()
		else:
			self.generateAllPaperTermRetrievalObjects()

	def generateSelectPaperTermRetrievalObject(self):
		for searchTerm in self.searchTermList:
			resultGetterForTerm = ResultGetterForTermSelectPapers(searchTerm, self.newspaperList,
																  self.yearRange,
																  self.progressTrackerThread,
																  self.connectionToDB)
			self.retrievalObjectList.append(resultGetterForTerm)

	def generateAllPaperTermRetrievalObjects(self):
		for searchTerm in self.searchTermList:
			resultGetterForTerm = ResultGetterForTermAllPapers(searchTerm, self.yearRange,
															   self.eliminateEdgePapers, self.progressTrackerThread,
															   self.connectionToDB)
			self.retrievalObjectList.append(resultGetterForTerm)

	def retrieveResults(self):
		for retrievalObject in self.retrievalObjectList:
			self.progressTrackerThread.setDiscoveryProgress(0)
			self.progressTrackerThread.setRetrievalProgress(0)
			currentTerm = retrievalObject.getSearchTerm()
			self.progressTrackerThread.setCurrentTerm(currentTerm)
			retrievalObject.runSearch()
		self.initiateSingleGraphManyData()
		self.sendTopPapersToRequestThread()


	def initiateSingleGraphManyData(self):
		grapher = GraphJSONmaker(self.requestID, self.connectionToDB, splitPapers=self.paperTrendLines,
								 splitTerms=self.termTrendLines)
		grapher.makeGraphJSON()
		graphJSON = grapher.getGraphJSON()
		self.progressTrackerThread.setGraphJSON(graphJSON)

	def sendTopPapersToRequestThread(self):
		self.topPaperList = [resultBundle.getTopTenPapers() for resultBundle in self.retrievalObjectList]
		self.progressTrackerThread.setTopPapers(self.topPaperList)
