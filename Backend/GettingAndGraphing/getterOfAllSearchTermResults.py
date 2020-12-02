import csv
import re
import sys
import shutil
import os
from multiprocessing import Pool, cpu_count

from Backend.GettingAndGraphing.dictionaryMaker import DictionaryMaker
from Backend.GettingAndGraphing.getterOfAllResultsFromPaper import *

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class GallicaSearch:

	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, **kwargs):
		self.lowYear = None
		self.highYear = None
		self.isYearRange = None
		self.baseQuery = None
		self.recordNumber = None
		self.numberQueriesToGallica = None
		self.isNoDictSearch = None
		self.defaultPaperDictionary = None
		self.progress = 0
		self.strictYearRange = strictYearRange
		self.totalResults = 0
		self.newspaper = newspaper
		self.newspaperDictionary = {}
		self.chunkedNewspaperDictionary = {}
		self.collectedQueries = []
		self.searchTerm = searchTerm
		self.topPapers = []
		self.topTenPapers = []
		self.numResultsForEachPaper = {}
		self.establishYearRange(yearRange)
		self.establishRecordNumber(kwargs)
		self.parseNewspaperDictionary()
		self.establishStrictness()
		self.buildQuery()

		self.paperNameCounts = []

		self.fileName = self.determineFileName()

	def checkIfFileAlreadyInDirectory(self):
		return os.path.isfile(os.path.join("../CSVdata", self.fileName))

	def runQuery(self):
		if self.checkIfFileAlreadyInDirectory():
			print("File exists in directory, skipping.")
		else:
			self.findTotalResults()
			self.runSearch()

	def establishRecordNumber(self, kwargs):
		if "recordNumber" in kwargs:
			self.recordNumber = kwargs["recordNumber"]

	def getTopTenPapers(self):
		return self.topTenPapers

	def getFileName(self):
		return self.fileName

	def getSearchTerm(self):
		return self.searchTerm

	def getYearRange(self):
		return "{0}-{1}".format(self.lowYear, self.highYear)

	def getCollectedQueries(self):
		return self.collectedQueries

	@staticmethod
	def sendQuery(queryToSend, **kwargs):
		if kwargs['startRecord'] is None:
			startRecord = 1
		else:
			startRecord = kwargs['startRecord']
		if kwargs['numRecords'] is None:
			numRecords = 50
		else:
			numRecords = kwargs['numRecords']
		hunter = GallicaHunter(queryToSend, startRecord, numRecords)
		hunter.hunt()
		return hunter

	def packageQuery(self):
		if len(self.collectedQueries) != 0:
			self.generateTopTenPapers()
			self.makeCSVFile()
		else:
			pass

	def establishNumberQueries(self):
		if type(self.recordNumber) is int:
			self.numberQueriesToGallica = self.recordNumber // 50



	def makeCSVFile(self):
		with open(self.fileName, "w", encoding="utf8") as outFile:
			writer = csv.writer(outFile)
			writer.writerow(["date", "journal", "url"])
			for csvEntry in self.collectedQueries:
				writer.writerow(csvEntry)
		shutil.move(self.fileName, os.path.join("../CSVdata", self.fileName))

	def determineFileName(self):
		nameOfFile = ''
		if self.newspaper == "all":
			nameOfFile = self.searchTerm + "-all-"
		else:
			for paper in self.newspaper:
				nameOfFile = paper + "-"
			nameOfFile = nameOfFile[0:len(nameOfFile)-1]
			wordsInQuery = self.searchTerm.split(" ")
			for word in wordsInQuery:
				nameOfFile = nameOfFile + word
		if self.isYearRange:
			nameOfFile = nameOfFile + str(self.lowYear) + "." + str(self.highYear)
		nameOfFile = nameOfFile + ".csv"
		return nameOfFile

	@staticmethod
	def reportProgress(iteration, total, part):
		progress = str(((iteration / total) * 100))
		print("{0}% complete {1}          ".format(progress[0:5], part), end="\r")
		sys.stdout.flush()
		if iteration == total:
			print()

	# Good time to parse errors in formatting too
	def establishStrictness(self):
		if self.strictYearRange in ["ya", "True", "true", "yes", "absolutely"]:
			self.strictYearRange = True
		else:
			self.strictYearRange = False

	def checkIfHitDateinQueryRange(self, dateToCheck):
		yearList = dateToCheck.split("-")
		lower = int(yearList[0])
		higher = int(yearList[1])
		if lower < self.lowYear and higher > self.highYear:
			return True
		else:
			return False

	# What if list of papers?
	def parseNewspaperDictionary(self):
		dicParser = DictionaryMaker(self.newspaper, [self.lowYear, self.highYear], self.strictYearRange)
		self.newspaperDictionary = dicParser.getDictionary()

	def establishYearRange(self, yearRange):
		yearRange = re.split(r'[;,\-\s*]', yearRange)
		if len(yearRange) == 2:
			self.lowYear = int(yearRange[0])
			self.highYear = int(yearRange[1])
			self.isYearRange = True
		else:
			self.isYearRange = False

	def buildQuery(self):
		if self.isYearRange:
			if self.newspaper == "noDict":
				self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and (gallica adj "{' \
								 '{searchWord}}") and (dc.type all "fascicule") sortby dc.date/sort.ascending '
			else:
				self.baseQuery = '(dc.date >= "{firstYear}" and dc.date <= "{secondYear}") and ((arkPress all "{{{{' \
								 'newsKey}}}}") and (gallica adj "{{searchWord}}")) sortby dc.date/sort.ascending '
			self.baseQuery = self.baseQuery.format(firstYear=str(self.lowYear), secondYear=str(self.highYear))
		else:
			if self.newspaper == "noDict":
				self.baseQuery = '(gallica adj "{searchWord}") and (dc.type all "fascicule") sortby dc.date/sort.ascending'
			else:
				self.baseQuery = 'arkPress all "{{newsKey}}" and (gallica adj "{searchWord}") sortby dc.date/sort.ascending'
		self.baseQuery = self.baseQuery.format(searchWord=self.searchTerm)

	def runSearch(self):
		pass

	def findTotalResults(self):
		pass

	def updateDictionaries(self):
		self.newspaperDictionary.clear()
		for i in range(10):
			self.topTenPapers.append(["",0])
		for nameCountCode in self.paperNameCounts:
			paperName = nameCountCode[0]
			paperCount = nameCountCode[1]
			paperCode = nameCountCode[2]
			self.updateTopTenPapers(paperName, paperCount)
			self.newspaperDictionary.update({paperName : paperCode})
			self.numResultsForEachPaper.update({paperName : paperCount})
			self.sumUpTotalResults(paperCount)

	def updateTopTenPapers(self, name, count):
		for i in range(10):
			currentIndexCount = self.topTenPapers[i][1]
			if count > currentIndexCount:
				self.topTenPapers.insert(i, [name, count])
				del(self.topTenPapers[10:])
				break

	def generateTopTenPapers(self):
		dictionaryFile = "{0}-{1}".format("TopPaperDict", self.fileName)
		with open(os.path.join("../CSVdata", dictionaryFile), "w", encoding="utf8") as outFile:
			writer = csv.writer(outFile)
			for newspaper in self.topTenPapers:
				writer.writerow([newspaper])

	def sumUpTotalResults(self, toAdd):
		self.totalResults = self.totalResults + toAdd

	def makeChunkedDictionary(self, chunkSize):
		listOfSubDicts = []
		initialList = []
		for paper in self.newspaperDictionary:
			initialList.append(paper)
		currentIndex = 0
		for i in range(ceil((len(self.newspaperDictionary) / chunkSize)) - 1):
			subDict = {}
			subList = initialList[currentIndex:currentIndex+chunkSize]
			currentIndex = currentIndex + chunkSize
			for paper in subList:
				subDict[paper] = self.newspaperDictionary[paper]
			listOfSubDicts.append(subDict)
		subDict = {}
		subList = initialList[currentIndex:]
		for paper in subList:
			subDict[paper] = self.newspaperDictionary[paper]
		listOfSubDicts.append(subDict)
		self.chunkedNewspaperDictionary = listOfSubDicts



class FullSearchWithinDictionary(GallicaSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange)

	def runSearch(self):
		self.createWorkersForSearch()

	def createWorkersForSearch(self):
		processes = cpu_count()
		with Pool(processes) as pool:
			for result in pool.imap_unordered(self.sendWorkersToSearch, self.newspaperDictionary):
				paperName = result[0]
				resultList = result[1]
				numberResultsForEntirePaper = result[2]
				self.collectedQueries = self.collectedQueries + resultList
				self.progress = self.progress + numberResultsForEntirePaper
				GallicaSearch.reportProgress(self.progress, self.totalResults,
											 "retrieving results for '{0}'".format(self.searchTerm))
				self.numResultsForEachPaper.update({paperName: numberResultsForEntirePaper})

	def sendWorkersToSearch(self, newspaper):
		numberResultsInPaper = self.numResultsForEachPaper[newspaper]
		newspaperCode = self.newspaperDictionary[newspaper]
		newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
		newspaperHuntOverseer = UnlimitedOverseerOfNewspaperHunt(newspaperQuery, numberResultsInPaper)
		newspaperHuntOverseer.scourPaper()
		return [newspaper, newspaperHuntOverseer.getResultList(), newspaperHuntOverseer.getNumValidResults()]

	def findTotalResults(self):
		self.createWorkersForFindingTotalResults()

	def createWorkersForFindingTotalResults(self):
		processes = cpu_count()
		pool = Pool(processes)
		chunkSize = 30
		self.makeChunkedDictionary(chunkSize)
		totalIterations = ceil(len(self.newspaperDictionary) / chunkSize)
		try:
			for i, result in enumerate(pool.imap_unordered(self.findNumberResults, self.chunkedNewspaperDictionary), 1):
				GallicaSearch.reportProgress(i, totalIterations,
											 "establishing total results for '{0}'".format(self.searchTerm))
				self.paperNameCounts = self.paperNameCounts + result
			pool.close()
			pool.join()
			self.updateDictionaries()
		except Exception as error:
			print(error)
			raise

	def findNumberResults(self, newspapers):
		gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
		adapter = TimeoutAndRetryHTTPAdapter(timeout=2.5)
		gallicaHttpSession.mount("https://", adapter)
		gallicaHttpSession.mount("http://", adapter)
		paperCounts = []
		for newspaper in newspapers:
			newspaperCode = newspapers[newspaper]
			newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
			hunterForTotalNumberOfQueryResults = GallicaHunter(newspaperQuery, 1, 1, gallicaHttpSession)
			numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
			if numberResultsForNewspaper != 0:
				paperCounts.append([newspaper, numberResultsForNewspaper, newspaperCode])
		return paperCounts



class FullSearchNoDictionary(GallicaSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, recordNumber):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange, recordNumber)

	def runSearch(self):
		theBigQuery = self.baseQuery
		numProcessedResults = 0
		startRecord = 1
		while self.totalResults > numProcessedResults:
			batchHunter = self.sendQuery(theBigQuery, startRecord=startRecord, numRecords=50)
			startRecord = startRecord + 50
			results = batchHunter.getResultList()
			numPurged = batchHunter.getNumberPurgedResults()
			self.collectedQueries = self.collectedQueries + results
			numProcessedResults = numProcessedResults + len(results) + numPurged

	def findTotalResults(self):
		hunterForTotalNumberOfQueryResults = GallicaHunter(self.baseQuery, 1, 1)
		self.totalResults = hunterForTotalNumberOfQueryResults.establishTotalHits(self.baseQuery, False)

	# make list of newspapers with number results. Do at the end of all queries (since # results updated during lower level runs)



