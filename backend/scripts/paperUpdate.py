import concurrent.futures

from requests_toolbelt import sessions
from scripts.utils.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter

from scripts.gallicaRecordBatch import GallicaPaperRecordBatch


class PaperUpdate:

    # TODO: split into multiple classes
    def __init__(self, gallicaSession=None):
        self.query = ''
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

    def initGallicaSession(self):
        self.session = sessions.BaseUrlSession("https://gallica.bnf.fr/SRU")
        adapter = TimeoutAndRetryHTTPAdapter()
        self.session.mount("https://", adapter)
