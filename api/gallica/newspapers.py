import concurrent.futures
import datetime
import psycopg2
from math import ceil

from timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from requests_toolbelt import sessions
from recordBatch import PaperRecordBatch


class Newspapers:

    def __init__(self, dbConnection):
        gallicaHttpSession = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter()
        gallicaHttpSession.mount("https://", adapter)
        gallicaHttpSession.mount("http://", adapter)
        self.session = gallicaHttpSession
        self.query = ''
        self.connectionToDB = dbConnection
        self.papers = []
        self.connection = conn
        self.paperDictAsJSON = {}

    def fetchAllGallicaPapers(self):
        self.query = '(dc.type all "fascicule")'
        self.beginPaperQueries()

    def beginPaperQueries(self):
        numPapers = self.getNumPapers()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            for batch in executor.map(self.fetchBatchPapersAtIndex,
                                      range(1, numPapers, 50)):
                self.papers.extend(batch)

    def fetchBatchPapersAtIndex(self, index):
        batch = PaperRecordBatch(self.query,
                                 self.session,
                                 startRecord=index
                                 )
        records = batch.getRecordBatch()
        return records

    def getNumPapers(self):
        self.query = '(dc.type all "fascicule")'
        tempBatch = PaperRecordBatch(
            self.query,
            self.session,
            numRecords=1
        )
        numResults = tempBatch.getNumResults()
        return numResults

    def addPaperToDBbyCode(self, code):
        metadata = self.fetchMetadataFromCode(code)
        if metadata:
            title = metadata[0]
            code = metadata[1]
            date = metadata[2]
        else:
            return None
        self.addMetadataToDB(title, code, date)

    def fetchMetadataFromCode(self, code):
        self.query = f'arkPress all "{code}_date"'
        batch = PaperRecordBatch(
            self.query,
            self.session,
            numRecords=1)
        result = batch.getRecordBatch()
        if result:
            record = result[0]
            title = record['title']
            code = record['code']
            date = record['date']
            return [title, code, date]
        else:
            return None

    def addMetadataToDB(self,
                        code,
                        title,
                        date=None):
        cursor = self.connectionToDB.cursor()
        cursor.execute(
            """
            INSERT INTO papers (title, date, code) 
                VALUES (%s, %s, %s);
        """, (title, date, code))

    def getPapersSimilarToKeyword(self, keyword):
        with self.connectionToDB.cursor() as curs:
            keyword = keyword.lower()
            curs.execute("""
                SELECT title, code
                    FROM papers 
                    WHERE LOWER(title) LIKE %(keyword)s
                    ORDER BY title LIMIT 20;
            """, {'paperNameSearchString': '%' + keyword + '%'})
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
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        paperGetter = Newspapers(conn)
        paperGetter.fetchAllGallicaPapers()
    finally:
        if conn is not None:
            conn.close()
