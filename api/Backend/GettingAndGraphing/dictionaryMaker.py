import psycopg2


class DictionaryMaker():
	def __init__(self, newspaperSetting, dbConnection):
		self.newspaperList = newspaperSetting
		self.dictionary = {}
		self.tupleEntryList = None
		self.dbConnection = dbConnection

	def getDictionary(self):
		self.establishNewspaperDictionaryOfSpecificNewspapers()
		return self.dictionary

	def establishNewspaperDictionaryOfSpecificNewspapers(self):
		for paper in self.newspaperList:
			try:
				SQL = """
					SELECT paperName, paperCode FROM papers WHERE paperName = %s
					;
					"""
				cursor = self.dbConnection.cursor()
				cursor.execute(SQL, (paper,))
				self.tupleEntryList = cursor.fetchall()
				self.parseTuplesIntoDictionary()
			except psycopg2.DatabaseError as e:
				print(e)

	def parseTuplesIntoDictionary(self):
		for tupleEntry in self.tupleEntryList:
			paperName = tupleEntry[0]
			paperCode = tupleEntry[1]
			self.dictionary[paperName] = paperCode
