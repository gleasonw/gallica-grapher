import concurrent.futures
import io

from requests_toolbelt import sessions
from scripts.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter
from scripts.psqlconn import PSQLconn

from scripts.gallicaRecordBatch import GallicaPaperRecordBatch


class Newspaper:

    # TODO: split into multiple classes
    def __init__(self, gallicaSession=None):
        self.query = ''
        self.papersSimilarToKeyword = []
        self.paperRecords = []
        self.dbConnection = PSQLconn().getConn()
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

    def fetchTheseMax20PaperRecords(self, paperCodes):
        formattedPaperCodes = [f"{paperCode[0]}_date" for paperCode in paperCodes]
        self.query = 'arkPress all "' + '" or arkPress all "'.join(formattedPaperCodes) + '"'
        batch = GallicaPaperRecordBatch(
            self.query,
            self.session,
            numRecords=20)
        return batch.getRecords()

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
                    self.paperRecords.extend(batch)

    def fetchBatchPapersAtIndex(self, index):
        batch = GallicaPaperRecordBatch(
            self.query,
            self.session,
            startRecord=index)
        records = batch.getRecords()
        return records

    def getNumPapersOnGallica(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        tempBatch = GallicaPaperRecordBatch(
            self.query,
            self.session,
            numRecords=1)
        numResults = tempBatch.getNumResults()
        return numResults

    def copyPapersToDB(self):
        with self.dbConnection.cursor() as curs:
            csvStream = self.generateCSVstream()
            curs.copy_from(csvStream, 'papers', sep='|')

    def generateCSVstream(self):

        def cleanCSVvalue(value):
            if value is None:
                return r'\N'
            return str(value).replace('|', '\\|')

        csvFileLikeObject = io.StringIO()
        for paperRecord in self.paperRecords:
            dateRange = paperRecord.getDate()
            lowYear = dateRange[0]
            highYear = dateRange[1]
            csvFileLikeObject.write('|'.join(map(cleanCSVvalue, (
                paperRecord.getPaperTitle(),
                lowYear,
                highYear,
                paperRecord.isContinuous(),
                paperRecord.getPaperCode()
            ))) + '\n')
        csvFileLikeObject.seek(0)
        return csvFileLikeObject

    def getPapersSimilarToKeyword(self, keyword):

        def paperDataToJSON(similarPapers):
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

        with self.dbConnection.cursor() as curs:
            keyword = keyword.lower()
            curs.execute("""
                SELECT title, code, startdate, enddate
                    FROM papers 
                    WHERE LOWER(title) LIKE %(paperNameSearchString)s
                    ORDER BY title LIMIT 20;
            """, {'paperNameSearchString': '%' + keyword + '%'})
            papersSimilarToKeyword = curs.fetchall()
            return paperDataToJSON(papersSimilarToKeyword)

    def initGallicaSession(self):
        self.session = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter()
        self.session.mount("https://", adapter)


if __name__ == '__main__':
    newspaper = Newspaper()
    newspaper.sendAllGallicaPapersToDB()
