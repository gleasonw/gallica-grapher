from dbops.connContext import getConn


class PaperLocalSearch:

    def select_continuous_papers(self, start_year, end_year, limit):
        bigger_year = max(start_year, end_year)
        smaller_year = min(start_year, end_year)
        bigger_year = bigger_year or 9999
        smaller_year = smaller_year or 0
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
            args = (smaller_year, bigger_year, limit,)
        else:
            args = (smaller_year, bigger_year,)
        conn = getConn()
        with conn.cursor() as curs:
            curs.execute(query, args)
            continuous_papers = curs.fetchall()
            return paperDataToJSON(continuous_papers)

    def selectPapersSimilarToKeyword(self, keyword):
        dbConn = getConn()
        with dbConn.cursor() as curs:
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
        dbConn = getConn()
        startDate = startDate or 0
        endDate = endDate or 9999
        with dbConn.cursor() as curs:
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
