import psycopg2


class DictionaryMaker():
	def __init__(self, newspaperSetting, yearRange, eliminateEdgePapers):
		self.newspaperSetting = newspaperSetting
		self.yearRange = yearRange
		self.isNoDictSearch = None
		self.dictionary = {}
		self.tupleEntryList = None
		self.eliminateEdgePapers = eliminateEdgePapers
		self.parseYearRange()

	def parseYearRange(self):
		if self.yearRange is not None:
			self.yearRange[0] = '{0}-01-01'.format(self.yearRange[0])
			self.yearRange[1] = '{0}-01-01'.format(self.yearRange[1])

	def getDictionary(self):
		self.parse()
		return self.dictionary

	def parse(self):
		conn = None
		try:
			conn = psycopg2.connect(
				host="localhost",
				database="postgres",
				user="postgres"
			)
			cursor = conn.cursor()
			firstPaper = self.newspaperSetting[0]
			if firstPaper in ["noDict", "unlimited", "finalForm"]:
				pass
				#gimme everything you have
			elif firstPaper in ["all", "full", "complete"]:
				if self.eliminateEdgePapers:
					self.establishYearStrictNewspaperDictionary(cursor)
				else:
					self.establishYearLooseNewspaperDictionary(cursor)
			else:
				self.establishNewspaperDictionaryOfSpecificNewspapers(cursor)

		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			raise
		finally:
			if conn is not None:
				conn.close()

	def establishYearStrictNewspaperDictionary(self, cursor):
		SQL = """
			SELECT paperName, paperCode
				FROM papers
					WHERE 
						startYear > (%s) and endYear < (%s)
			;
			"""
		yearTuple = (self.yearRange[0], self.yearRange[1])
		cursor.execute(SQL, yearTuple)
		self.tupleEntryList = cursor.fetchall()
		self.parseTuplesIntoDictionary()

	def establishYearLooseNewspaperDictionary(self, cursor):
		SQL = """
			SELECT paperName, paperCode
				FROM papers
				WHERE startYear BETWEEN (%s) AND (%s) OR
					endYear BETWEEN (%s) AND (%s)
			;
			"""
		yearTuple = (self.yearRange[0], self.yearRange[1], self.yearRange[0], self.yearRange[1])
		cursor.execute(SQL, yearTuple)
		self.tupleEntryList = cursor.fetchall()
		self.parseTuplesIntoDictionary()

	def establishNewspaperDictionaryOfSpecificNewspapers(self, cursor):
		SQL = """
			SELECT paperName, paperCode
				FROM papers
					WHERE 
						paperName IN %s
			;
			"""
		cursor.execute(SQL, (tuple(self.newspaperSetting),))
		self.tupleEntryList = cursor.fetchall()
		self.parseTuplesIntoDictionary()

	def parseTuplesIntoDictionary(self):
		for tupleEntry in self.tupleEntryList:
			paperName = tupleEntry[0]
			paperCode = tupleEntry[1]
			self.dictionary[paperName] = paperCode
