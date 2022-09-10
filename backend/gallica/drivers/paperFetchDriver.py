class PaperFetchDriver:

    def __init__(self, parse, getCQLstringsFor, makeQuery, fetchNoTrack):
        self.parse = parse
        self.getCQLstringsFor = getCQLstringsFor
        self.makeQuery = makeQuery
        self.fetchNoTrack = fetchNoTrack

    def getNumResults(self):
        numResults = self.xmlRoot.find(
            "{http://www.loc.gov/zing/srw/}numberOfRecords")
        if numResults is not None:
            numResults = numResults.text
            numResults = int(numResults)
        return numResults

    def fetchPaperRecordsForCodes(self, paperCodes):
        batchedURLs = self.getCQLstringsFor(paperCodes)
        recordDataQueries = self.generateSelectCodeQueries(batchedURLs)
        publishingRangeQueries = self.generateRangeQueries(paperCodes)
        xml = self.fetchNoTrack(recordDataQueries)
        records = self.parse(self, xml)

    def generateSelectCodeQueries(self, batchedURLs):
        baseUrl = '"https://gallica.bnf.fr/SRU'
        for url in batchedURLs:
            yield self.makeQuery(
                url=url,
                startIndex=1,
                numRecords=50,
                collapsing=True
            )

    def generateRangeQueries(self, codes):
        for code in codes:
            yield self.makeQuery(
                url=code,
                startIndex=1,
                numRecords=1,
                collapsing=False
            )

    def fetchAllPaperRecords(self):
        cql = 'dc.type all "fascicule" and ocrquality > "050.00"'
        numPapers = self.getNumPapersOnGallica()
        indices = range(1, numPapers, 50)
        queryIndices = [(cql, index) for index in indices]
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