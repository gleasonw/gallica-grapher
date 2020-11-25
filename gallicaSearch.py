import csv
import re
import sys
import shutil
import os
from gallicaHunter import GallicaHunter
from multiprocessing import Pool, Manager, Lock, cpu_count
from overseerOfNewspaperHunt import *


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
		return os.path.isfile(os.path.join("./CSVdata", self.fileName))

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

	def generateTopTenPapers(self):
		def newsCountSort(theList):
			return theList[1]

		for newspaper in self.newspaperDictionary:
			numResults = self.numResultsForEachPaper[newspaper]
			self.topPapers.append([newspaper, numResults])

		self.topPapers.sort(key=newsCountSort, reverse=True)

		for i in range(10):
			newspaper = self.topPapers[i][0]
			self.topTenPapers.append(newspaper)
			count = self.topPapers[i][1]
			place = i + 1

		dictionaryFile = "{0}-{1}".format("TopPaperDict", self.fileName)

		with open(os.path.join("./CSVdata", dictionaryFile), "w", encoding="utf8") as outFile:
			writer = csv.writer(outFile)
			for newspaper in self.topTenPapers:
				writer.writerow([newspaper])

	def makeCSVFile(self):

		with open(self.fileName, "w", encoding="utf8") as outFile:
			writer = csv.writer(outFile)
			writer.writerow(["date", "journal", "url"])
			for csvEntry in self.collectedQueries:
				writer.writerow(csvEntry)
		shutil.move(os.path.join("./", self.fileName), os.path.join("./CSVdata", self.fileName))

	def determineFileName(self):
		if self.newspaper == "all":
			nameOfFile = self.searchTerm + "-all-"
		else:
			nameOfFile = self.newspaper + "-"
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
		here = os.path.dirname(os.path.abspath(__file__))
		self.defaultPaperDictionary = os.path.join(here, "AvailableJournals 1777-1950.csv")
		if self.newspaper == "noDict":
			self.isNoDictSearch = True
		else:
			self.isNoDictSearch = False
			if self.strictYearRange:
				if self.newspaper == "all":
					self.establishStrictNewspaperDictionary()
				else:
					self.establishStrictTrimmedNewspaperDictionary()
			else:
				if self.newspaper == "all":
					self.establishLooseNewspaperDictionary()
				else:
					self.establishLooseTrimmedNewspaperDictionary()

	def establishStrictNewspaperDictionary(self):
		with open(self.defaultPaperDictionary, "r", encoding="utf8") as inFile:
			reader = csv.reader(inFile)
			next(reader)
			for newspaperHit in reader:
				publicationRange = newspaperHit[1]
				if not self.checkIfHitDateinQueryRange(publicationRange):
					continue
				else:
					gallicaCode = newspaperHit[4]
					newspaperName = newspaperHit[0]
					self.newspaperDictionary.update({newspaperName: gallicaCode})

	def establishLooseNewspaperDictionary(self):
		with open(self.defaultPaperDictionary, "r", encoding="utf8") as inFile:
			reader = csv.reader(inFile)
			next(reader)
			for newspaperHit in reader:
				gallicaCode = newspaperHit[4]
				newspaperName = newspaperHit[0]
				self.newspaperDictionary.update({newspaperName: gallicaCode})

	def establishStrictTrimmedNewspaperDictionary(self):
		# Gonna have to fix this eventually. Need better capability to find the right newspapers in the CSV. Database
		# time?
		with open(self.defaultPaperDictionary, "r", encoding="utf8") as inFile:
			reader = csv.reader(inFile)
			next(reader)
			for newspaperHit in reader:
				publicationRange = newspaperHit[1]
				newspaperName = newspaperHit[0]
				if (not self.checkIfHitDateinQueryRange(publicationRange)) or (self.newspaper != newspaperName):
					continue
				else:
					gallicaCode = newspaperHit[4]
					self.newspaperDictionary.update({newspaperName: gallicaCode})

	def establishLooseTrimmedNewspaperDictionary(self):
		# Gonna have to fix this eventually. Need better capability to find the right newspapers in the CSV. Database
		# time?
		with open(self.defaultPaperDictionary, "r", encoding="utf8") as inFile:
			reader = csv.reader(inFile)
			next(reader)
			for newspaperHit in reader:
				newspaperName = newspaperHit[0]
				if newspaperName != self.newspaper:
					continue
				else:
					gallicaCode = newspaperHit[4]
					self.newspaperDictionary.update({newspaperName: gallicaCode})

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
		for nameCountCode in self.paperNameCounts:
			paperName = nameCountCode[0]
			paperCount = nameCountCode[1]
			paperCode = nameCountCode[2]
			self.newspaperDictionary.update({paperName : paperCode})
			self.numResultsForEachPaper.update({paperName : paperCount})
			self.sumUpTotalResults(paperCount)

	def sumUpTotalResults(self, toAdd):
		self.totalResults = self.totalResults + toAdd



class FullSearchWithinDictionary(GallicaSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange)

	def runSearch(self):
		self.createWorkersForSearch()

	def createWorkersForSearch(self):
		processes = cpu_count()
		with Pool(processes) as pool:
			chunkSize = ceil(len(self.newspaperDictionary) / processes)
			for result in pool.imap_unordered(self.sendWorkersToSearch, self.newspaperDictionary, chunksize=chunkSize):
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
		for i, result in enumerate(pool.imap_unordered(self.findNumberResults, self.newspaperDictionary, chunksize=20),1):
			GallicaSearch.reportProgress(i, len(self.newspaperDictionary), "finding total results")
			numResults = result[1]
			if numResults != 0:
				self.paperNameCounts.append(result)
		pool.close()
		pool.join()
		self.updateDictionaries()

	def findNumberResults(self, newspaper):
		newspaperCode = self.newspaperDictionary[newspaper]
		newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
		hunterForTotalNumberOfQueryResults = GallicaHunter(newspaperQuery, 1, 1)
		numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
		return [newspaper, numberResultsForNewspaper, newspaperCode]



class RecordLimitedSearchWithinDictionary(GallicaSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, recordNumber):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange, recordNumber=recordNumber)

	def runSearch(self):
		totalNumberValidResults = 0
		resultsLeftToGet = self.recordNumber
		for newspaper in self.newspaperDictionary:
			numberResultsInPaper = self.numResultsForEachPaper[newspaper]
			newspaperCode = self.newspaperDictionary[newspaper]
			newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
			numberResultsWanted = min(resultsLeftToGet, numberResultsInPaper)
			newspaperHuntOverseer = LimitedOverseerOfNewspaperHunt(newspaperQuery, numberResultsInPaper,
																   numberResultsWanted)
			newspaperHuntOverseer.scourPaper()
			currentNumberValidResults = newspaperHuntOverseer.getNumberValidResults()
			# probably redundant
			if newspaperHuntOverseer.getNumberValidResults() == 0:
				break
			else:
				totalNumberValidResults = totalNumberValidResults + currentNumberValidResults
				if totalNumberValidResults > self.recordNumber:
					break
			self.collectedQueries = self.collectedQueries + newspaperHuntOverseer.getResultList()
			resultsLeftToGet = resultsLeftToGet - currentNumberValidResults
			if resultsLeftToGet == 0:
				break

	def findTotalResults(self):
		toBeSaved = []
		progressMeter = 0

		for newspaper in self.newspaperDictionary:
			progressMeter = progressMeter + 1
			GallicaSearch.reportProgress(progressMeter, len(self.newspaperDictionary), "finding total results")
			newspaperCode = self.newspaperDictionary[newspaper]
			newspaperQuery = self.baseQuery.format(newsKey=newspaperCode)
			hunterForTotalNumberOfQueryResults = GallicaHunter(newspaperQuery, 1, 1)
			numberResultsForNewspaper = hunterForTotalNumberOfQueryResults.establishTotalHits(newspaperQuery, False)
			self.totalResults = self.totalResults + numberResultsForNewspaper
			if self.totalResults >= self.recordNumber:
				break
			elif numberResultsForNewspaper != 0:
				self.numResultsForEachPaper.update({newspaper: numberResultsForNewspaper})
		for newspaper in self.newspaperDictionary:
			if newspaper not in toBeSaved:
				uselessPaper = newspaper
				self.newspaperDictionary.pop(uselessPaper)



class RecordLimitedSearchNoDictionary(GallicaSearch):
	def __init__(self, searchTerm, newspaper, yearRange, strictYearRange, recordNumber):
		super().__init__(searchTerm, newspaper, yearRange, strictYearRange, recordNumber=recordNumber)

	def runSearch(self):
		theBigQuery = self.baseQuery
		numProcessedResults = 0
		startRecord = 1
		maximumResults = min(self.totalResults, self.recordNumber)
		while maximumResults > numProcessedResults:
			amountRemaining = self.recordNumber - numProcessedResults
			if amountRemaining >= 50:
				numRecords = 50
			else:
				numRecords = amountRemaining
			batchHunter = self.sendQuery(theBigQuery, startRecord=startRecord, numRecords=numRecords)
			startRecord = startRecord + 50
			results = batchHunter.getResultList()
			numPurged = batchHunter.getNumberPurgedResults()
			self.collectedQueries = self.collectedQueries + results
			numProcessedResults = numProcessedResults + len(results) + numPurged

	def findTotalResults(self):
		hunterForTotalNumberOfQueryResults = GallicaHunter(self.baseQuery, 1, 1)
		self.totalResults = hunterForTotalNumberOfQueryResults.establishTotalHits(self.baseQuery, False)



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
