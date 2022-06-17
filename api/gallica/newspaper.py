import concurrent.futures
import io

from requests_toolbelt import sessions
from gallica.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from gallica.db import DB

from gallica.recordBatch import PaperRecordBatch


class Newspaper:

    #TODO: split into multiple classes
    def __init__(self, gallicaSession=None):
        self.query = ''
        self.papersSimilarToKeyword = []
        self.paperRecords = []
        self.dbConnection = DB().getConn()
        if not gallicaSession:
            self.initGallicaSession()
        else:
            self.session = gallicaSession

    def sendTheseGallicaPapersToDB(self, paperCodes):
        for i in range(0, len(paperCodes), 15):
            self.query = 'arkPress all "' + '" or arkPress all "'.join(paperCodes[i:i+15]) + '"'

    def sendAllGallicaPapersToDB(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        self.fetchAllPapersFromGallica()
        self.copyPapersToDB()
        self.dbConnection.close()

    def fetchAllPapersFromGallica(self):
        with self.session:
            numPapers = self.getNumPapersOnGallica()
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                for batch in executor.map(self.fetchBatchPapersAtIndex,
                                          range(1, numPapers, 50)):
                    print(batch)
                    self.paperRecords.extend(batch)

    def fetchBatchPapersAtIndex(self, index):
        batch = PaperRecordBatch(
            self.query,
            self.session,
            startRecord=index)
        records = batch.getRecordBatch()
        return records

    def getNumPapersOnGallica(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        tempBatch = PaperRecordBatch(
            self.query,
            self.session,
            numRecords=1)
        numResults = tempBatch.getNumResults()
        return numResults

    def cleanCSVvalue(self, value):
        if value is None:
            return r'\N'
        return str(value).replace('|', '\\|')

    def copyPapersToDB(self):
        with self.dbConnection.cursor() as curs:
            csvFileLikeObject = io.StringIO()
            for paperRecord in self.paperRecords:
                dateRange = paperRecord.getDate()
                lowYear = dateRange[0]
                highYear = dateRange[1]
                csvFileLikeObject.write('|'.join(map(self.cleanCSVvalue, (
                    paperRecord.getTitle(),
                    lowYear,
                    highYear,
                    paperRecord.getContinuous(),
                    paperRecord.getPaperCode()
                ))) + '\n')
            csvFileLikeObject.seek(0)
            curs.copy_from(csvFileLikeObject, 'papers', sep='|')

    def fetchThese15PaperRecords(self, paperCodes):
        self.query =
        batch = PaperRecordBatch(
            self.query,
            self.session,
            numRecords=1)
        result = batch.getRecordBatch()
        if result:
            self.paperRecords.extend(result)

    def insertPaper(self, paper):
        title = paper.getTitle()
        dateRange = paper.getDate()
        continuous = paper.getContinuous()
        code = paper.getPaperCode()
        lowYear = dateRange[0]
        highYear = dateRange[1]

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
            self.papersSimilarToKeyword = curs.fetchall()
            return self.nameCodeDataToJSON()

    def nameCodeDataToJSON(self):
        namedPaperCodes = []
        for paperTuple in self.papersSimilarToKeyword:
            paper = paperTuple[0]
            code = paperTuple[1]
            namedPair = {'paper': paper, 'code': code}
            namedPaperCodes.append(namedPair)
        return {'paperNameCodes': namedPaperCodes}

    def initGallicaSession(self):
        self.session = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter()
        self.session.mount("https://", adapter)
