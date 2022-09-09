import concurrent.futures

from requests_toolbelt import sessions
from scripts.utils.timeoutAndRetryHTTPAdapter import TimeoutAndRetryHTTPAdapter

from gallicaRecordBatch import GallicaPaperRecordBatch
from scripts.cqlSelectStringForPapers import CQLSelectStringForPapers

NUM_WORKERS = 50


class PaperRecordFetch:

    def __init__(self, gallicaSession=None):
        self.query = ''
        if not gallicaSession:
            self.initGallicaSession()
        else:
            self.session = gallicaSession

    def fetchPaperRecordsForCodes(self, paperCodes):
        batchedQueries = CQLSelectStringForPapers(paperCodes).cqlSelectStrings
        queryIndices = [(query, 1) for query in batchedQueries]
        paperRecords = self.fetchPapersConcurrently(queryIndices)
        return paperRecords

    def fetchAllPaperRecords(self):
        query = 'dc.type all "fascicule" and ocrquality > "050.00"'
        numPapers = self.getNumPapersOnGallica()
        indices = range(1, numPapers, 50)
        queryIndices = [(query, index) for index in indices]
        allRecords = self.fetchPapersConcurrently(queryIndices)
        return allRecords

    def fetchPapersConcurrently(self, queryIndices):
        records = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            for batch in executor.map(
                    self.fetchBatchPapersAtIndex,
                    queryIndices):
                records.extend(batch)
        return records

    def fetchBatchPapersAtIndex(self, queryIndex):
        print(f'fetching query {queryIndex[0]} at index {queryIndex[1]}')
        batch = GallicaPaperRecordBatch(
            query=queryIndex[0],
            session=self.session,
            startRecord=queryIndex[1])
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
