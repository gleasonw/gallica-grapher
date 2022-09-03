import concurrent.futures

from requests_toolbelt import sessions
from scripts.utils.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter

from scripts.gallicaRecordBatch import GallicaPaperRecordBatch
from scripts.cqlSelectStringForPapers import CQLSelectStringForPapers

NUM_WORKERS = 50


class PaperRecordFetch:

    def __init__(self, gallicaSession=None):
        self.query = ''
        if not gallicaSession:
            self.initGallicaSession()
        else:
            self.session = gallicaSession

    def fetchRecordDataForCodes(self, paperCodes):
        paperRecords = []
        with self.session:
            for i in range(0, len(paperCodes), 20):
                batchOf20 = self.fetchTheseMax20PaperRecords(paperCodes[i:i + 20])
                paperRecords.extend(batchOf20)
        return paperRecords

    def fetchTheseMax20PaperRecords(self, paperCodes):
        self.query = CQLSelectStringForPapers(paperCodes).cqlSelectStrings[0]
        batch = GallicaPaperRecordBatch(
            self.query,
            self.session,
            numRecords=20)
        return batch.getRecords()

    def fetchAllPaperRecordsOnGallica(self):
        self.query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        allRecords = self.runThreadedPaperFetch()
        return allRecords

    def runThreadedPaperFetch(self):
        records = []
        with self.session:
            numPapers = self.getNumPapersOnGallica()
            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
                for batch in executor.map(
                        self.fetchBatchPapersAtIndex,
                        range(1, numPapers, 50)):
                    records.extend(batch)
        return records

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
