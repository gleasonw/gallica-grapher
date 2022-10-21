from query import OccurrenceQuery
from query import ArkQueryForNewspaperYears
from query import PaperQuery
from query import ContentQuery
from gallica.params import Params


class QueryFactory:

    def __init__(self, gallicaAPI, parse, numResultsCallback=None):
        self.gallicaAPI = gallicaAPI
        self.parse = parse
        self.numResultsCallback = numResultsCallback

    def indexEachQueryFromNumResults(self, queries) -> list:
        indexedQueries = []
        for query, numResults in self.getNumResultsForEachQuery(queries):
            for i in range(0, numResults, 50):
                baseData = query.getEssentialDataForMakingAQuery()
                baseData['startIndex'] = i
                baseData["numRecords"] = 50
                indexedQueries.append(
                    self.makeQuery(**baseData)
                )
        return indexedQueries

    def getNumResultsForEachQuery(self, queries) -> list:
        responses = self.gallicaAPI.get(queries)
        numResultsForQueries = [
            (response.query, self.parse.getNumResults(response.xml))
            for response in responses
        ]
        self.numResultsCallback and self.numResultsCallback(numResultsForQueries)
        return numResultsForQueries

    def makeQuery(self, **kwargs):
        raise NotImplementedError


class OccurrenceQueryFactory(QueryFactory):

    def buildQueriesForArgs(self, args):
        baseQueries = self.buildForBundle(
            Params(
                terms=args['terms'],
                codes=args['codes'],
                startDate=args['startDate'],
                endDate=args['endDate'],
                link=(args['linkTerm'], args['linkDistance']),
                grouping=args['grouping'],
                numRecords=args['numRecords'],
                startIndex=args['startIndex']
            )
        )
        if args['grouping'] == 'all':
            return self.indexEachQueryFromNumResults(baseQueries)
        else:
            return baseQueries

    def buildForBundle(self, bundle):
        if codes := bundle.getCodeBundles():
            return self.buildWithCodeBundles(bundle, codes)
        else:
            return self.buildNoCodeBundles(bundle)

    def buildWithCodeBundles(self, bundle, codeBundles):
        return [
            self.makeQuery(term, startDate, endDate, bundle, codes)
            for term in bundle.getTerms()
            for startDate, endDate in bundle.getDateGroupings()
            for codes in codeBundles
        ]

    def buildNoCodeBundles(self, bundle):
        return [
            self.makeQuery(term, startDate, endDate, bundle)
            for term in bundle.getTerms()
            for startDate, endDate in bundle.getDateGroupings()
        ]

    def makeQuery(self, term, startDate, endDate, searchMetaData, startIndex=0, numRecords=1, codes=None):
        codes = codes or []
        return OccurrenceQuery(
            term=term,
            searchMetaData=searchMetaData,
            startIndex=startIndex,
            numRecords=numRecords,
            codes=codes,
            startDate=startDate,
            endDate=endDate,
        )


class PaperQueryFactory(QueryFactory):

    def buildQueriesForArgs(self, args):
        codes = args.get('codes')
        return self.buildSRUQueriesForCodes(codes) if codes else self.buildSRUQueriesForAllRecords()

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
        return self.indexEachQueryFromNumResults([
            PaperQuery(
                startIndex=0,
                numRecords=1
            )
        ])

    def buildArkQueriesForCodes(self, codes):
        return [
            ArkQueryForNewspaperYears(code=code)
            for code in codes
        ]

    def makeQuery(self, codes, startIndex, numRecords):
        return PaperQuery(
            startIndex=startIndex,
            numRecords=numRecords,
            codes=codes
        )


class ContentQueryFactory:

    def buildQueryForArkAndTerm(self, ark, term):
        return ContentQuery(
            ark=ark,
            term=term
        )

