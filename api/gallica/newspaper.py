import concurrent.futures
import psycopg2
from requests_toolbelt import sessions
from .timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter

from .recordBatch import PaperRecordBatch


class Newspaper:

    def __init__(self):
        self.query = ''
        self.dbConnection = None
        self.session = None
        self.papers = []
        self.initDBConnection()
        self.initGallicaSession()

    def sendGallicaPapersToDB(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        self.fetchAllPapersFromGallica()
        self.dbConnection.close()

    def fetchAllPapersFromGallica(self):
        numPapers = self.getNumPapersOnGallica()
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            for batch in executor.map(self.fetchBatchPapersAtIndex,
                                      range(1, numPapers, 50)):
                for paper in batch:
                    self.insertPaper(paper)

    def fetchBatchPapersAtIndex(self, index):
        batch = PaperRecordBatch(self.query,
                                 self.session,
                                 startRecord=index)
        records = batch.getRecordBatch()
        return records

    def getNumPapersOnGallica(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        tempBatch = PaperRecordBatch(self.query,
                                     self.session,
                                     numRecords=1)
        numResults = tempBatch.getNumResults()
        return numResults

    def addPaperToDBbyCode(self, code):
        record = self.fetchPaperRecordFromCode(code)
        if record:
            self.insertPaper(record)
            self.dbConnection.close()
        else:
            raise FileNotFoundError

    def fetchPaperRecordFromCode(self, code):
        self.query = f'arkPress all "{code}_date"'
        batch = PaperRecordBatch(self.query,
                                 self.session,
                                 numRecords=1)
        result = batch.getRecordBatch()
        if result:
            record = result[0]
            return record
        else:
            return None

    def insertPaper(self, paper):
        title = paper.getTitle()
        dateRange = paper.getDate()
        continuous = paper.getContinuous()
        code = paper.getPaperCode()
        lowYear = dateRange[0]
        highYear = dateRange[-1]

        with self.dbConnection.cursor() as curs:
            curs.execute(
                """
                INSERT INTO papers (title, startdate, enddate, continuous, code) 
                    VALUES (%s, %s, %s, %s, %s);
                """, (title, lowYear, highYear, continuous, code))

    def getPapersSimilarToKeyword(self, keyword):
        with self.dbConnection.cursor() as curs:
            keyword = keyword.lower()
            curs.execute("""
                SELECT title, code
                    FROM papers 
                    WHERE LOWER(title) LIKE %(paperNameSearchString)s
                    ORDER BY title LIMIT 20;
            """, {'paperNameSearchString': '%' + keyword + '%'})
            self.papers = curs.fetchall()
            return self.nameCodeDataToJSON()

    def nameCodeDataToJSON(self):
        namedPaperCodes = []
        for paperTuple in self.papers:
            paper = paperTuple[0]
            code = paperTuple[1]
            namedPair = {'paper': paper, 'code': code}
            namedPaperCodes.append(namedPair)
        return {'paperNameCodes': namedPaperCodes}

    #TODO: Closing connection?
    def initDBConnection(self):
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        self.dbConnection = conn

    def initGallicaSession(self):
        self.session = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter()
        self.session.mount("https://", adapter)

if __name__ == "__main__":
    papers = Newspaper()
    print(papers.sendGallicaPapersToDB())