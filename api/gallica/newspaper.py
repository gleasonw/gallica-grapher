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
        with self.session:
            self.fetchPapersDataInBatches(paperCodes)
        self.copyPapersToDB()

    def fetchPapersDataInBatches(self, paperCodes):
        for i in range(0, len(paperCodes), 20):
            batchOf20 = self.fetchTheseMax20PaperRecords(paperCodes[i:i + 20])
            self.paperRecords.extend(batchOf20)

    def sendAllGallicaPapersToDB(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        self.fetchAllPapersFromGallica()
        self.copyPapersToDB()
        self.dbConnection.close()

    def fetchAllPapersFromGallica(self):
        with self.session:
            numPapers = self.getNumPapersOnGallica()
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                for batch in executor.map(
                        self.fetchBatchPapersAtIndex,
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
            csvStream = self.generateCSVstream()
            curs.copy_from(csvStream, 'papers', sep='|')

    def generateCSVstream(self):
        csvFileLikeObject = io.StringIO()
        for paperRecord in self.paperRecords:
            dateRange = paperRecord.getDate()
            lowYear = dateRange[0]
            highYear = dateRange[1]
            csvFileLikeObject.write('|'.join(map(self.cleanCSVvalue, (
                paperRecord.getTitle(),
                lowYear,
                highYear,
                paperRecord.isContinuous(),
                paperRecord.getPaperCode()
            ))) + '\n')
        csvFileLikeObject.seek(0)
        return csvFileLikeObject


    def fetchTheseMax20PaperRecords(self, paperCodes):
        self.query = 'arkPress all "' + '_date" or arkPress all "'.join(paperCodes) + '_date"'
        batch = PaperRecordBatch(
            self.query,
            self.session,
            numRecords=20)
        return batch.getRecordBatch()

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
