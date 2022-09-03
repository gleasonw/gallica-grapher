from utils.psqlconn import PSQLconn


class PaperLocalSearch:

    def __init__(self):
        self.dbConnection = PSQLconn().getConn()
        self.cursor = self.dbConnection.cursor()

    def selectPapersContinuousOverRange(self, startYear, endYear):
        with self.dbConnection.cursor() as curs:
            curs.execute("""
                SELECT title, code, startdate, enddate
                    FROM papers
                    WHERE startdate <= %s
                    AND enddate >= %s
                    AND continuous;
                """, (startYear, endYear,))
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

    def getNumPapersInRange(self, startYear, endYear):
        with self.dbConnection.cursor() as curs:
            curs.execute("""
                SELECT COUNT(*) FROM papers
                    WHERE startdate BETWEEN %s AND %s
                    OR enddate BETWEEN %s AND %s;
                """, (startYear, endYear, startYear, endYear))
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
