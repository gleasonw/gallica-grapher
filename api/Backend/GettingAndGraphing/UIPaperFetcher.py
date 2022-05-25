import psycopg2


class UIPaperFetcher:
	def __init__(self, conn):
		self.papers = []
		self.connection = conn
		self.paperDictAsJSON = {}

	def getPapersLikeString(self, paperNameSearchString):
		with self.connection.cursor() as curs:
			paperNameSearchString = paperNameSearchString.lower()
			curs.execute("""
				SELECT papername, papercode FROM papers WHERE LOWER(papername) LIKE %(paperNameSearchString)s
					ORDER BY papername LIMIT 20;
			""", {'paperNameSearchString': '%' + paperNameSearchString + '%'})
			self.papers = curs.fetchall()
			return self.nameCodeDataToJSON()

	def allPaperDataToJSON(self):
		for i, paperTuple in enumerate(self.papers):
			identifier = paperTuple[0]
			paper = paperTuple[1]
			startYear = paperTuple[2]
			endYear = paperTuple[3]
			JSONentry = {'paperName': paper,
						 'identifier': identifier,
						 'startyear': startYear,
						 'endyear': endYear}
			self.paperDictAsJSON.update({i: JSONentry})
		return self.paperDictAsJSON

	def nameCodeDataToJSON(self):
		namedPaperCodes = []
		for paperTuple in self.papers:
			paper = paperTuple[0]
			code = paperTuple[1]
			namedPair = {'paper': paper, 'code': code}
			namedPaperCodes.append(namedPair)
		return {'paperNameCodes': namedPaperCodes}



if __name__ == "__main__":
	conn = None
	query = 'Le peti'
	try:
		conn = psycopg2.connect(
			host="localhost",
			database="gallicagrapher",
			user="wgleason",
			password="ilike2play"
		)
		getter = UIPaperFetcher(conn)
		availablePapers = getter.getPapersLikeString(query)
		pass
	finally:
		if conn is not None:
			conn.close()
