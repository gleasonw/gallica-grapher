import concurrent.futures
import datetime
import psycopg2
from math import ceil

import lxml.etree
from Backend.GettingAndGraphing.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from lxml import etree
from requests_toolbelt import sessions


class GallicaPaperQuery:

	@staticmethod
	def removeNonDigitYearsFromDateRange(dateRangeToStandardize):
		splitDates = dateRangeToStandardize.split("-")
		cleanedDates = []
		for date in splitDates:
			try:
				int(date)
				cleanedDates.append(date)
			except ValueError:
				continue
		return cleanedDates

	@staticmethod
	def prepPaperDateRangeForDBEntry(publicationRange=None):
		if publicationRange:
			standardizedRange = GallicaPaperQuery.removeNonDigitYearsFromDateRange(publicationRange)
			if len(standardizedRange) == 2:
				startDate = standardizedRange[0]
				endDate = standardizedRange[1]
			elif len(standardizedRange) == 1:
				startDate = standardizedRange[0]
				endDate = None
			else:
				startDate = None
				endDate = None
		else:
			startDate = None
			endDate = None
		return startDate, endDate

	@staticmethod
	def addPaperMetadataToDB(paperName=None, paperCode=None, startYear=None, endYear=None, cursor=None):
		if startYear:
			startYear = datetime.date(int(startYear), 1, 1)
		if endYear:
			endYear = datetime.date(int(endYear), 1, 1)
		cursor.execute("""
							INSERT INTO papers (papername, startyear, endyear, papercode) 
								VALUES (%s, %s, %s, %s);
							""", (paperName, startYear, endYear, paperCode))

	def __init__(self, dbConnection):
		gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
		adapter = TimeoutAndRetryHTTPAdapter()
		gallicaHttpSession.mount("https://", adapter)
		gallicaHttpSession.mount("http://", adapter)
		self.session = gallicaHttpSession
		self.query = ''
		self.connectionToDB = dbConnection

	def addPaperToDBbyCode(self, paperCode):
		paperName, startDate, endDate = self.getPaperMetadataFromCode(paperCode)
		try:
			cursor = self.connectionToDB.cursor()
			self.addPaperMetadataToDB(paperName, paperCode, startDate, endDate, cursor)
		except psycopg2.DatabaseError:
			raise

	def getPaperMetadataFromCode(self, paperCode):
		self.query = f'arkPress all "{paperCode}_date" sortby dc.date/sort.ascending '
		result = self.sendPaperQueryToGallica(1)
		if result:
			paperInfo = result[0]
			paperName = paperInfo[0]
			startDate, endDate = GallicaPaperQuery.prepPaperDateRangeForDBEntry(publicationRange=paperInfo[1])
			return paperName, startDate, endDate
		else:
			return None, None, None

	def addMostNewspapersOnGallicaToDB(self):
		self.query = '(dc.type all "fascicule") sortby dc.date/sort.ascending'
		parameters = dict(version=1.2, operation="searchRetrieve", exactSearch=False, collapsing=True,
						  query=self.query, startRecord=0, maximumRecords=1)
		response = self.session.get("", params=parameters)
		root = etree.fromstring(response.content)
		numberHits = int(root[2].text)
		iterations = ceil(numberHits / 50)
		startRecordList = []
		try:
			cursor = self.connectionToDB.cursor()
			for i in range(iterations):
				startRecordList.append((i * 50) + 1)
			with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
				for result in executor.map(self.sendPaperQueryToGallica, startRecordList):
					if result:
						for paperData in result:
							startYear, endYear = GallicaPaperQuery.prepPaperDateRangeForDBEntry(
								publicationRange=paperData[1])
							paperName = paperData[0]
							print(paperName)
							paperCode = paperData[2]
							GallicaPaperQuery.addPaperMetadataToDB(paperName, paperCode, startYear, endYear, cursor)
		except psycopg2.DatabaseError as e:
			print(e)

	def sendPaperQueryToGallica(self, startRecord):
		parameters = dict(version=1.2, operation="searchRetrieve", exactSearch=False, collapsing=True,
						  query=self.query, startRecord=startRecord, maximumRecords=50)
		response = self.session.get("", params=parameters)
		try:
			root = etree.fromstring(response.content)
			data = self.getPaperMetadataFromXML(root)
		except lxml.etree.ParseError as e:
			print(response.content)
			return None
		return data

	def getPaperMetadataFromXML(self, targetXMLroot):
		results = []
		for queryHit in targetXMLroot.iter("{http://www.loc.gov/zing/srw/}record"):
			data = queryHit[2][0]
			journalName = data.find('{http://purl.org/dc/elements/1.1/}title').text
			if journalName is None:
				raise FileNotFoundError
			journalCodeContainer = data.find('{http://purl.org/dc/elements/1.1/}relation').text
			if journalCodeContainer:
				journalCode = journalCodeContainer[-11:]
			else:
				raise FileNotFoundError
			#It's ok if there is no date associated with a paper
			#TODO: If there is no 'date' attached to the result, is it somewhere else?
			try:
				journalDate = data.find('{http://purl.org/dc/elements/1.1/}date').text
			except AttributeError:
				journalDate = None
			results.append([journalName, journalDate, journalCode])
		return results


if __name__ == "__main__":
	conn = None
	try:
		conn = psycopg2.connect(
			host="localhost",
			database="gallicagrapher",
			user="wgleason",
			password="ilike2play"
		)
		conn.set_session(autocommit=True)
		paperGetter = GallicaPaperQuery(conn)
		paperGetter.addMostNewspapersOnGallicaToDB()
	finally:
		if conn is not None:
			conn.close()
