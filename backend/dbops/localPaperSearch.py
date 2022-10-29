from dbops.connContext import getConn


class PaperLocalSearch:

    def __init__(self):
        self.dbConnection = getConn()
        self.cursor = self.dbConnection.cursor()

    def selectPapersContinuousOverRange(self, firstInputYear, secondInputYear, limit):
        biggerYear = max(firstInputYear, secondInputYear)
        smallerYear = min(firstInputYear, secondInputYear)
        query = """
        SELECT title, code, startdate, enddate
        FROM papers
        WHERE startdate <= %s
        AND enddate >= %s
        AND continuous
        """
        if limit:
            limit = int(limit)
            query += " LIMIT %s"
            args = (smallerYear, biggerYear, limit,)
        else:
            args = (smallerYear, biggerYear,)
        with self.dbConnection.cursor() as curs:
            curs.execute(query, args)
            papersContinuousOverRange = curs.fetchall()
            return paperDataToJSON(papersContinuousOverRange)

    def selectPapersSimilarToKeyword(self, keyword):
        with self.dbConnection.cursor() as curs:
            keyword = keyword.lower()
            curs.execute("""
                SELECT title, code, startdate, enddate
                    FROM papers 
                    WHERE LOWER(title) LIKE %(paperNameSearchString)s
                    ORDER BY title DESC LIMIT 20;
            """, {'paperNameSearchString': '%' + keyword + '%'})
            papersSimilarToKeyword = curs.fetchall()
            return paperDataToJSON(papersSimilarToKeyword)

    def getNumPapersInRange(self, startDate, endDate):
        with self.dbConnection.cursor() as curs:
            curs.execute("""
                SELECT COUNT(*) FROM papers
                    WHERE startdate BETWEEN %s AND %s
                        OR enddate BETWEEN %s AND %s
                        OR (startdate < %s AND enddate > %s)
                    ;
                """, (
                startDate,
                endDate,
                startDate,
                endDate,
                startDate,
                endDate))
            numPapersOverRange = curs.fetchone()
            return numPapersOverRange[0]


def paperDataToJSON(similarPapers) -> dict:
    papers = []
    for paperData in similarPapers:
        title = paperData[0]
        code = paperData[1]
        startDate = paperData[2]
        endDate = paperData[3]
        paper = {
            'title': title,
            'code': code,
            'startDate': startDate,
            'endDate': endDate
        }
        papers.append(paper)
    return {'paperNameCodes': papers}
