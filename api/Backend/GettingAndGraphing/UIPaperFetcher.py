import psycopg2


class UIPaperFetcher:
	def __init__(self):
		self.papers = []
		self.papers = self.queryDatabaseForPapers()
		self.paperDictAsJSON = {}
		self.transformPapersIntoJSON()

	def queryDatabaseForPapers(self):
		conn = None
		try:
			conn = psycopg2.connect(
				host="localhost",
				database="postgres",
				user="wglea",
				password="ilike2play"
			)
			cursor = conn.cursor()
			query = """
			SELECT paperCode, paperName, startYear, endYear FROM papers
				ORDER BY paperName;
			"""
			cursor.execute(query)
			return cursor.fetchall()
		finally:
			if conn is not None:
				conn.close()

	def getPapers(self):
		return self.paperDictAsJSON

	def transformPapersIntoJSON(self):
		i = 0
		for paperTuple in self.papers:
			identifier = paperTuple[0]
			paper = paperTuple[1]
			startYear = paperTuple[2]
			endYear = paperTuple[3]
			JSONentry = {'paperName': paper,
						 'identifier': identifier,
						 'startyear': startYear,
						 'endyear': endYear}
			self.paperDictAsJSON.update({i: JSONentry})
			i += 1
