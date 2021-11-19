import re
from lxml import etree


class GallicaHunter:
	def __init__(self, query, startRecord, numRecords, session):
		self.dateJournalIdentifierResults = []
		self.query = query
		self.queryHitNumber = 0
		self.startRecord = startRecord
		self.numPurgedResults = 0
		self.numRecords = numRecords
		self.session = session

	def establishTotalHits(self, query, collapseResults):
		if collapseResults:
			collapseSetting = "true"
		else:
			collapseSetting = "disabled"
		parameters = dict(version=1.2, operation="searchRetrieve", collapsing=collapseSetting, exactSearch="false",
						  query=query, startRecord=0, maximumRecords=1)
		response = self.session.get("", params=parameters)
		print(response.status_code)
		root = etree.fromstring(response.content)
		numResults = int(root[2].text)
		return numResults

	@staticmethod
	def standardizeSingleDate(dateToStandardize):
		yearMonDay = re.compile(r"^\d{4}-\d{2}-\d{2}$")
		twoYears = re.compile(r"^\d{4}-\d{4}$")
		oneYear = re.compile(r"^\d{4}$")
		oneYearOneMon = re.compile(r"^\d{4}-\d{2}$")
		if not yearMonDay.match(dateToStandardize):
			if oneYear.match(dateToStandardize):
				return dateToStandardize + "-01-01"
			elif oneYearOneMon.match(dateToStandardize):
				return dateToStandardize + "-01"
			elif twoYears.match(dateToStandardize):
				dates = dateToStandardize.split("-")
				lowerDate = int(dates[0])
				higherDate = int(dates[1])
				if higherDate - lowerDate <= 10:
					newDate = (lowerDate + higherDate) // 2
					return str(newDate) + "-01-01"
				else:
					return None
			else:
				return None
		else:
			return dateToStandardize

	def hunt(self):
		parameters = {"version": 1.2, "operation": "searchRetrieve", "query": self.query,
					  "startRecord": self.startRecord, "maximumRecords": self.numRecords, "collapsing": "disabled"}
		response = self.session.get("", params=parameters)
		print(response.status_code)
		root = etree.fromstring(response.content)
		self.hitListCreator(root)

	def hitListCreator(self, targetXMLroot):
		priorJournal = ''
		priorDate = ''
		for queryHit in targetXMLroot.iter("{http://www.loc.gov/zing/srw/}record"):
			self.queryHitNumber = self.queryHitNumber + 1
			data = queryHit[2][0]
			dateOfHit = data.find('{http://purl.org/dc/elements/1.1/}date').text
			dateOfHit = GallicaHunter.standardizeSingleDate(dateOfHit)
			if dateOfHit is not None:
				journalOfHit = data.find('{http://purl.org/dc/elements/1.1/}title').text
				if dateOfHit == priorDate and journalOfHit == priorJournal:
					self.numPurgedResults = self.numPurgedResults + 1
					continue
				else:
					identifierOfHit = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
					fullResult = [dateOfHit, journalOfHit, identifierOfHit]
					self.dateJournalIdentifierResults.append(fullResult)
					priorJournal = journalOfHit
					priorDate = dateOfHit
			else:
				self.numPurgedResults = self.numPurgedResults + 1
				continue

	def getNumberPurgedResults(self):
		return self.numPurgedResults

	def getResultList(self):
		return self.dateJournalIdentifierResults