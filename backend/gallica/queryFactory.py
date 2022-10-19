from query import OccurrenceQuery
from query import ArkQueryForNewspaperYears
from query import PaperQuery
from gallica.params import Params


class QueryFactory:

    def __init__(self, gallicaAPI, parse):
        self.gallicaAPI = gallicaAPI
        self.parse = parse

    def getNumResultsForEachQuery(self, queries) -> dict:
        responses = self.gallicaAPI.fetchAll(queries)
        numResultsForQueries = {}
        for response in responses:
            numRecordsForBaseCQL = self.parse.getNumRecords(response.xml)
            numResultsForQueries[response.query] = numRecordsForBaseCQL
        return numResultsForQueries

    def makeIndexedQueries(self, baseQueries) -> list:
        indexedQueries = []
        for query, numResults in baseQueries.items():
            for i in range(0, numResults, 50):
                baseData = query.getEssentialDataForMakingAQuery()
                baseData["startIndex"] = i
                baseData["numRecords"] = 50
                baseData["collapsing"] = False
                indexedQueries.append(
                    self.makeQuery(**baseData)
                )
        return indexedQueries

    def makeQuery(self, term, dates, bundle, codes=None):
        raise NotImplementedError


class OccurrenceQueryFactory(QueryFactory):
    def __init__(self):
        super().__init__()

    def buildQueriesForArgs(self, args):
        baseQueries = self.buildForBundle(
            Params(
                terms=args['terms'],
                codes=args['codes'],
                startDate=args['startDate'],
                endDate=args['endDate'],
                link=(args['linkTerm'], args['linkDistance']),
                grouping=args['searchType'],
                numRecords=args['numRecords'],
                startIndex=args['startIndex']
            )
        )
        return self.makeIndexedQueries(baseQueries) if args['grouping'] == 'all' else baseQueries

    def buildForBundle(self, bundle):
        if codes := bundle.getCodeBundles():
            return self.buildWithCodeBundles(bundle, codes)
        else:
            return self.buildNoCodeBundles(bundle)

    def buildWithCodeBundles(self, bundle, codeBundles):
        return [
            self.makeQuery(term, bundle, dates, codes)
            for term in bundle.getTerms()
            for dates in bundle.getDateGroupings()
            for codes in codeBundles
        ]

    def buildNoCodeBundles(self, bundle):
        return [
            self.makeQuery(term, dates, bundle)
            for term in bundle.getTerms()
            for dates in bundle.getDateGroupings()
        ]

    def makeQuery(self, term, ticket, dates, codes=None):
        codes = codes or []
        return OccurrenceQuery(
            term=term,
            ticket=ticket,
            startIndex=0,
            numRecords=1,
            collapsing=False,
            codes=codes,
            startDate=dates[0],
            endDate=dates[1]
        )


class PaperQueryFactory(QueryFactory):

    def __init__(self, gallicaAPI, parse):
        self.indexer = QueryIndexer(
            gallicaAPI=gallicaAPI,
            parse=parse,
            makeQuery=PaperQuery
        )

    def buildSRUQueriesForCodes(self, codes):
        sruQueries = []
        for i in range(0, len(codes), 10):
            codesForQuery = codes[i:i + 10]
            sruQuery = PaperQuery(
                startIndex=0,
                numRecords=10,
                codes=codesForQuery
            )
            sruQueries.append(sruQuery)
        return sruQueries

    def buildSRUQueriesForAllRecords(self):
        sruQuery = PaperQuery(
            startIndex=0,
            numRecords=1
        )
        numResults = self.indexer.getNumResultsForEachQuery([sruQuery])
        return self.indexer.makeIndexedQueries(numResults)

    def buildArkQueriesForCodes(self, codes):
        return [
            ArkQueryForNewspaperYears(code)
            for code in codes
        ]


class QueryIndexer:

    def __init__(self, gallicaAPI, parse, makeQuery):
        self.gallicaAPI = gallicaAPI
        self.parse = parse
        self.makeQuery = makeQuery

