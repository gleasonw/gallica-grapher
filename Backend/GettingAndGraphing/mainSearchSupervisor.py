from Backend.GettingAndGraphing.termSearch import *
from Backend.GettingAndGraphing.rGrapher import GallicaGrapher

import csv
import shutil
import os


class MultipleSearchTermHunt:

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

	def getAllResultBundlers(self):
		return self.searchTermResultList

	def runMultiTermQuery(self):
		for searchTerm in self.searchTermList:
			if self.newspaper[0] == "noDict":
				resultGetterForTerm = FullSearchNoDictionary(searchTerm, self.newspaper, self.yearRange,
															 self.strictYearRange, self.progressTrackerThread)
			else:
				resultGetterForTerm = FullSearchWithinDictionary(searchTerm, self.newspaper,
																 self.yearRange,
																 self.strictYearRange, self.progressTrackerThread)
			self.searchTermResultList.append(resultGetterForTerm)
			resultGetterForTerm.runQuery()
		self.createFilesForResultBundles()
		self.initiateGraphing()

	def initiateGraphing(self):
		if self.theKwargsForGraphingAndRecordNumber['uniqueGraphs']:
			if self.theKwargsForGraphingAndRecordNumber['samePage']:
				self.initiateSinglePageManyGraphs()
			else:
				self.initiateSingleGraphPerPage()
		else:
			self.initiateSingleGraphManyData()

	def createGGplotsForBundles(self):
		requestId = self.progressTrackerThread.getId()
		for resultBundle in self.searchTermResultList:
			fileName = resultBundle.getFileName()
			topTenPapers = resultBundle.getTopTenPapers()
			searchTerm = resultBundle.getSearchTerm()
			grapher = GallicaGrapher(fileName, topTenPapers, self.theKwargsForGraphingAndRecordNumber, requestId,
									 searchTerm)
			grapher.parseGraphSettings()
			self.listOfGraphers.append(grapher)

	def createFilesForResultBundles(self):
		for resultBundle in self.searchTermResultList:
			resultBundle.packageQuery()

	def initiateSingleGraphPerPage(self):
		self.createGGplotsForBundles()
		for grapher in self.listOfGraphers:
			grapher.plotGraphAndMakePNG()

	def initiateSingleGraphManyData(self):
		self.makeMultiTermFileName()
		self.createMassiveCSV()
		topTenPapers = []
		requestId = self.progressTrackerThread.getId()
		grapher = GallicaGrapher(self.bigFileName, topTenPapers, self.theKwargsForGraphingAndRecordNumber, requestId,
								 self.searchTermList)
		grapher.parseGraphSettings()
		grapher.plotGraphAndMakePNG()
		graphFileName = grapher.getFileName()
		graphFileName = "/static/{filename}".format(filename=graphFileName)
		self.progressTrackerThread.setImageRef(graphFileName)


	def initiateSinglePageManyGraphs(self):
		self.createGGplotsForBundles()
		self.makeMultiTermFileName()
		ggPlotList = []
		for grapher in self.listOfGraphers:
			ggPlotList.append(grapher.getGGplot())
		ggPlotList[0].arrangeGGplotsAndPlot(ggPlotList)

	def runMultiTermQueryWithDiffPapers(self):
		pass

	def createMassiveCSV(self):
		with open(self.bigFileName, "w", encoding="utf8", newline='') as outFile:
			writer = csv.writer(outFile)
			writer.writerow(['date', 'journal', 'url', 'term'])
			for resultBundle in self.searchTermResultList:
				resultList = resultBundle.getCollectedQueries()
				if len(resultList) == 0:
					termDataFileName = resultBundle.getFileName()
					term = resultBundle.getSearchTerm()
					filePath = os.path.join("/", termDataFileName)
					with open(filePath, "r", encoding="utf8") as inFile:
						reader = csv.reader(inFile)
						next(reader)
						for result in reader:
							writer.writerow(result + [term])
				else:
					for csvEntry in resultBundle.getCollectedQueries():
						searchTermOfResultBundle = resultBundle.searchTerm
						writer.writerow(csvEntry + [searchTermOfResultBundle])
		shutil.move(self.bigFileName, os.path.join("../CSVdata", self.bigFileName))

	def makeMultiTermFileName(self):
		for resultBundle in self.searchTermResultList:
			self.bigFileName = self.bigFileName + resultBundle.getSearchTerm() + "~"
		randomBundleForYearRange = self.searchTermResultList[0]
		self.bigFileName = self.bigFileName + randomBundleForYearRange.getYearRange()
		self.bigFileName = self.bigFileName + ".csv"
