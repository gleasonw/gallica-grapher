

class PaperSearchFactory:

    def __init__(
            self,
            dbLink,
            baseQueryMaker,
            parse,
            sruFetcher
    ):
        self.cql = CQLStringForPaperCodes()
        self.makeIndexer = lambda cql: AllQueryIndexer(cql)
        self.makeNumPapersQuery = lambda cql: NumPapersOnGallicaQuery(cql)

    def buildSRUQueriesForCodes(self, codes):
        cqlStrings = self.cql.build(codes)
        for cql in cqlStrings:
            yield PaperQuery(cql, startIndex=1)

    def buildARKQueriesForCodes(self, codes):
        queries = [ArkQueryForNewspaperYears(code) for code in codes]
        return queries

    def buildAllRecordsQueries(self) -> list:
        query = self.makeNumPapersQuery(
            'dc.type all "fascicule" and ocrquality > "050.00"'
        )
        indexer = self.makeIndexer([query])
        totalResults = fetchNumResultsForQueries(indexer.fetch, indexer.baseQueries, indexer.parse)
        queries = makeIndexedPaperQueries(indexer.baseQueries, totalResults)
        return queries
