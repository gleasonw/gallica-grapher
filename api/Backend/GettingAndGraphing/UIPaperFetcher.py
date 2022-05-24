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
				SELECT papername FROM papers WHERE LOWER(papername) LIKE %(paperNameSearchString)s
					ORDER BY papername;
			""", {'paperNameSearchString': '%' + paperNameSearchString + '%'})
			self.papers = curs.fetchall()
			return self.nameDataToJSON()

	def fullPaperDataToJSON(self):
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

	def nameDataToJSON(self):
		deTupledList = []
		for paper in self.papers:
			deTupledList.append(paper[0])
		return {'paperNames':deTupledList}


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
	finally:
		if conn is not None:
			conn.close()
