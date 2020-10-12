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

				else:
					resultGetterForTerm = FullSearchWithinDictionary(searchTerm, self.newspaper,
																			  self.yearRange,
																			  self.strictYearRange)
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

	def createFilesForResultBundles(self):
		for resultBundle in self.searchTermResultList:
			resultBundle.packageQuery()

	def initiateSingleGraphPerPage(self):
		self.createFilesForResultBundles()
		self.createGGplotsForBundles()
		for grapher in self.listOfGraphers:
			grapher.plotGraphAndMakePNG()

	def initiateSingleGraphManyData(self):
		self.createFilesForResultBundles()
		self.makeMultiTermFileName()
		self.createMassiveCSV()
		topTenPapers = []
		grapher = GallicaGrapher(self.bigFileName, topTenPapers, self.theKwargsForGraphingAndRecordNumber)
		grapher.parseGraphSettings()
		grapher.plotGraphAndMakePNG()

	def initiateSinglePageManyGraphs(self):
		self.createFilesForResultBundles()
		self.createGGplotsForBundles()
		self.makeMultiTermFileName()
		ggPlotList = []
		for grapher in self.listOfGraphers:
			ggPlotList.append(grapher.getGGplot())
		GallicaGrapher.arrangeGGplotsAndPlot(ggPlotList, self.bigFileName)

	def runMultiTermQueryWithDiffPapers(self):
		pass

	def createMassiveCSV(self):
		with open(self.bigFileName, "w", encoding="utf8") as outFile:
			writer = csv.writer(outFile)
			writer.writerow(['date','journal','url','term'])
			for resultBundle in self.searchTermResultList:
				resultList = resultBundle.getCollectedQueries()
				if len(resultList) == 0:
					termDataFileName = resultBundle.getFileName()
					term = resultBundle.getSearchTerm()
					filePath = os.path.join("./CSVdata", termDataFileName)
					with open(filePath, "r", encoding="utf8") as inFile:
						reader = csv.reader(inFile)
						next(reader)
						for result in reader:
							writer.writerow(result + [term])
				else:
					for csvEntry in resultBundle.getCollectedQueries():
						searchTermOfResultBundle = resultBundle.searchTerm
						writer.writerow(csvEntry + [searchTermOfResultBundle])
		shutil.move(self.bigFileName, os.path.join("./CSVdata", self.bigFileName))



	def makeMultiTermFileName(self):
		for resultBundle in self.searchTermResultList:
			self.bigFileName = self.bigFileName + resultBundle.getSearchTerm() + "~"
		randomBundleForYearRange = self.searchTermResultList[0]
		self.bigFileName = self.bigFileName + randomBundleForYearRange.getYearRange()
		self.bigFileName = self.bigFileName + ".csv"