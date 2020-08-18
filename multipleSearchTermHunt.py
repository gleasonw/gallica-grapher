from huntOverseer import HuntOverseer
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

	def runMultiTermQuery(self):
		for searchTerm in self.searchTermList:
			resultGetterForTerm = HuntOverseer(searchTerm, self.newspaper, self.yearRange, self.strictYearRange,
											   self.theKwargsForGraphingAndRecordNumber["recordNumber"])
			resultGetterForTerm.runQuery()
			self.searchTermResultList.append(resultGetterForTerm)
		self.initiateGraphing()

	def putTheResultsInFiles(self):
		for resultBundle in self.searchTermResultList:
			resultBundle.packageQuery()

	def initiateGraphing(self):
		if self.theKwargsForGraphingAndRecordNumber['uniqueGraphs'].lower() in ["true", "yup"]:
			if self.theKwargsForGraphingAndRecordNumber['samePage'].lower() in ["true", "yup"]:
				self.initiateSinglePageManyGraphs()
			else:
				self.initiateSingleGraphPerPage()
		else:
			self.initiateSingleGraphManyData()

	def initiateSingleGraphPerPage(self):
		self.putTheResultsInFiles(self)
		for resultBundle in self.searchTermList:
			fileName = resultBundle.getFileName()
			topTenPapers = resultBundle.getTopTenPapers()
			grapher = GallicaGrapher(fileName, topTenPapers, self.theKwargsForGraphingAndRecordNumber)
			grapher.parseGraphSettings()
			grapher.plotGraphAndMakePNG()

	def initiateSingleGraphManyData(self):
		self.createMassiveCSV()
		topTenPapers = []
		grapher = GallicaGrapher('massive.csv', topTenPapers, self.theKwargsForGraphingAndRecordNumber)
		grapher.parseGraphSettings()
		grapher.plotGraphAndMakePNG()

	def initiateSinglePageManyGraphs(self):
		self.createMassiveCSV()

	def runMultiTermQueryWithDiffPapers(self):
		pass

	def createMassiveCSV(self):
		with open("massive.csv", "w", encoding="utf8") as outFile:
			writer = csv.writer(outFile)
			writer.writerow(['date','journal','url','term'])
			for resultBundle in self.searchTermResultList:
				for csvEntry in resultBundle.collectedQueries:
					searchTermOfResultBundle = resultBundle.searchTerm
					writer.writerow(csvEntry + [searchTermOfResultBundle])
		shutil.move("massive.csv", os.path.join("./CSVdata", "massive.csv"))
