from gallica.query import OccurrenceQuery
from gallica.gallicaxmlparse import GallicaXMLparse
from gallica.query import ArkQueryForNewspaperYears
from gallica.query import PaperQuery
from gallica.query import ContentQuery
from gallica.params import Params


class QueryFactory:

    def __init__(self, gallicaAPI):
        self.gallicaAPI = gallicaAPI
        self.parser = GallicaXMLparse()

    def createIndexedQueriesFromRootQueries(self, queries, limit=None) -> list:
        queriesWithNumResults = ((query, limit) for query in queries) if limit else self.getNumResultsForEachQuery(queries)
        return self.indexQueriesWithNumResults(queriesWithNumResults)

    def indexQueriesWithNumResults(self, queriesWithNumResults):
        indexedQueries = []
        for query, numResults in queriesWithNumResults:
            for i in range(0, numResults, 50):
                baseData = query.getEssentialDataForMakingAQuery()
                baseData['startIndex'] = i
                baseData["numRecords"] = min(50, numResults - i)
                indexedQueries.append(
                    self.makeQuery(**baseData)
                )
        return indexedQueries

    def getNumResultsForEachQuery(self, queries) -> list:
        responses = self.gallicaAPI.get(queries)
        numResultsForQueries = [
            (response.query, self.parser.getNumRecords(response.xml))
            for response in responses
        ]
        return numResultsForQueries

    def makeQuery(self, **kwargs):
        raise NotImplementedError


class OccurrenceQueryFactory(QueryFactory):

    def buildQueriesFromQueryCounts(self, queryCounts):
        return self.indexQueriesWithNumResults(queryCounts)

    def buildQueriesForArgs(self, args):
        baseQueries = self.buildForParams(
            Params(**args)
        )
        if args['grouping'] == 'all':
            return self.buildIndexedQueriesFromArgs(
                args=args,
                baseQueries=baseQueries,
            )
        else:
            return baseQueries

    def buildForParams(self, params):
        if codes := params.getCodeBundles():
            return self.buildWithCodeBundles(params, codes)
        else:
            return self.buildNoCodeBundles(params)

    def buildWithCodeBundles(self, params, codeBundles):
        return [
            self.makeQuery(
                term=term,
                startDate=startDate,
                endDate=endDate,
                searchMetaData=params,
                codes=codes
            )
            for term in params.getTerms()
            for startDate, endDate in params.getDateGroupings()
            for codes in codeBundles
        ]

    def buildNoCodeBundles(self, bundle):
        return [
            self.makeQuery(term, startDate, endDate, bundle)
            for term in bundle.getTerms()
            for startDate, endDate in bundle.getDateGroupings()
        ]

    def buildIndexedQueriesFromArgs(self, args, baseQueries):
        if numDesiredRecords := args.get('numRecords'):
            return self.createIndexedQueriesFromRootQueries(
                queries=baseQueries,
                limit=int(numDesiredRecords)
            )
        else:
            return self.createIndexedQueriesFromRootQueries(baseQueries)

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
        return self.createIndexedQueriesFromRootQueries([
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

