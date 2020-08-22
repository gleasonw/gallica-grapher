from gallicaSearch import *
from gallicaGrapher import GallicaGrapher
import csv
import shutil
import os


# Different papers for each term? Oohhhh... only unlimited. Thank you.
class MultipleSearchTermHunt:

	def __init__(self, searchList, newspaper, yearRange, strictYearRange, **kwargs):
		self.searchTermList = searchList
		self.newspaper = newspaper
		self.yearRange = yearRange
		self.strictYearRange = strictYearRange
		self.searchTermResultList = []
		self.theKwargsForGraphingAndRecordNumber = kwargs
		self.listOfGraphers = []
		self.bigFileName = ''

	def runMultiTermQuery(self):
		for searchTerm in self.searchTermList:
			if self.newspaper == "noDict":
				if self.theKwargsForGraphingAndRecordNumber["recordNumber"] != 0:
					resultGetterForTerm = RecordLimitedSearchNoDictionary(searchTerm, self.newspaper, self.yearRange, self.strictYearRange,
													   self.theKwargsForGraphingAndRecordNumber["recordNumber"])
				else:
					resultGetterForTerm = FullSearchNoDictionary(searchTerm, self.newspaper, self.yearRange,
																		  self.strictYearRange)
			else:
				if self.theKwargsForGraphingAndRecordNumber["recordNumber"] != 0:
					resultGetterForTerm = RecordLimitedSearchWithinDictionary(searchTerm, self.newspaper, self.yearRange,
																		  self.strictYearRange,
																		  self.theKwargsForGraphingAndRecordNumber[
																			  "recordNumber"])
					resultGetterForTerm.findTotalResults()

				else:
					resultGetterForTerm = FullSearchWithinDictionary(searchTerm, self.newspaper,
																			  self.yearRange,
																			  self.strictYearRange)
					resultGetterForTerm.findTotalResults()
			resultGetterForTerm.runQuery()
			self.searchTermResultList.append(resultGetterForTerm)
		self.initiateGraphing()

	def initiateGraphing(self):
		if self.theKwargsForGraphingAndRecordNumber['uniqueGraphs'].lower() in ["true", "yup"]:
			if self.theKwargsForGraphingAndRecordNumber['samePage'].lower() in ["true", "yup"]:
				self.initiateSinglePageManyGraphs()
			else:
				self.initiateSingleGraphPerPage()
		else:
			self.initiateSingleGraphManyData()

	def createGGplotsForBundles(self):
		for resultBundle in self.searchTermResultList:
			fileName = resultBundle.getFileName()
			topTenPapers = resultBundle.getTopTenPapers()
			grapher = GallicaGrapher(fileName, topTenPapers, self.theKwargsForGraphingAndRecordNumber)
			grapher.parseGraphSettings()
			self.listOfGraphers.append(grapher)

	def initiateSingleGraphPerPage(self):
		self.createGGplotsForBundles()
		for grapher in self.listOfGraphers:
			grapher.plotGraphAndMakePNG()

	def initiateSingleGraphManyData(self):
		self.createMassiveCSV()
		topTenPapers = []
		grapher = GallicaGrapher('massive.csv', topTenPapers, self.theKwargsForGraphingAndRecordNumber)
		grapher.parseGraphSettings()
		grapher.plotGraphAndMakePNG()

	def initiateSinglePageManyGraphs(self):
		self.createGGplotsForBundles()
		self.makeMultiTermFileName()
		ggPlotList = []
		for grapher in self.listOfGraphers:
			ggPlotList.append(grapher.getGGplot())
		GallicaGrapher.arrangeGGplotsAndPlot(ggPlotList, self.bigFileName)

	def runMultiTermQueryWithDiffPapers(self):
		pass

	def createMassiveCSV(self):
		with open("massive.csv", "w", encoding="utf8") as outFile:
			writer = csv.writer(outFile)
			writer.writerow(['date','journal','url','term'])
			for resultBundle in self.searchTermResultList:
				for csvEntry in resultBundle.getCollectedQueries():
					searchTermOfResultBundle = resultBundle.searchTerm
					writer.writerow(csvEntry + [searchTermOfResultBundle])
		shutil.move("massive.csv", os.path.join("./CSVdata", "massive.csv"))

	def makeMultiTermFileName(self):
		for resultBundle in self.searchTermResultList:
			self.bigFileName = self.bigFileName + resultBundle.getSearchTerm() + "~"
		randomBundleForYearRange = self.searchTermResultList[0]
		self.bigFileName = self.bigFileName + randomBundleForYearRange.getYearRange()
		self.bigFileName = self.bigFileName + ".png"