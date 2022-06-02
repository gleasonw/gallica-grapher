import concurrent.futures
import datetime
import psycopg2
from math import ceil

import lxml.etree
from timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from lxml import etree
from requests_toolbelt import sessions
from recordBatch import PaperRecordBatch


class GallicaPaperQuery:

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
		result = self.fetchBatchPapersAtIndex(1)
		self.parsePaperRecord(result)

	def addMostNewspapersOnGallicaToDB(self):
		self.query = '(dc.type all "fascicule")'
		self.beginPaperQueries()

	def beginPaperQueries(self):
		numPapers = self.getNumPapers()
		with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
			for record in executor.map(self.fetchBatchPapersAtIndex, range(1, numPapers, 50)):
				self.parsePaperRecord(record)

	def getNumPapers(self):
		pass

	def __init__(self, root):
		self.root = root

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
