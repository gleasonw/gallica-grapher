from gallicaGetter.query import OccurrenceQuery
from gallicaGetter.gallicaxmlparse import GallicaXMLparse
from gallicaGetter.query import ArkQueryForNewspaperYears
from gallicaGetter.query import PaperQuery
from gallicaGetter.query import ContentQuery
from gallicaGetter.dateGrouping import DateGrouping
import logging

NUM_CODES_PER_BUNDLE = 10


class QueryBuilder:

    def __init__(self, gallicaAPI):
        self.gallicaAPI = gallicaAPI
        self.parser = GallicaXMLparse()

    def createIndexedQueriesFromRootQueries(self, queries, limit=None) -> list:
        queriesWithNumResults = ((query, limit) for query in queries) if limit else self.getNumResultsForEachQuery(queries)
        return self.indexQueriesWithNumResults(queriesWithNumResults)

    def indexQueriesWithNumResults(self, queriesWithNumResults):
        indexedQueries = []
        for query, numResults in queriesWithNumResults:
            numResults = int(numResults)
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


class OccurrenceQueryBuilder(QueryBuilder):

    def buildQueriesForArgs(self, args):
        baseQueries = self.buildBaseQueriesFromArgs(args)
        if args['grouping'] == 'all':
            return self.createIndexedQueriesFromRootQueries(
                queries=baseQueries,
                limit=args.get('numRecords')
            )
        return baseQueries

    def buildBaseQueriesFromArgs(self, args):
        terms = args.get('terms')
        codes = args.get('codes')
        if terms is None:
            raise ValueError('terms must be provided --> get(terms="...") or get(terms=["...", ...])')
        if not isinstance(terms, list):
            terms = [terms]
        if codes and not isinstance(codes, list):
            codes = [codes]
        return [
            self.makeQuery(
                term=term,
                startDate=startDate,
                endDate=endDate,
                searchMetaData=args,
                codes=codeBundle
            )
            for term in terms
            for startDate, endDate in DateGrouping(
                args.get('startDate'),
                args.get('endDate'),
                args.get('grouping')
            )
            for codeBundle in self.bundleCodesTogether(codes)
        ]

    def bundleCodesTogether(self, codes):
        return [None] if codes is None or len(codes) == 0 else [
            codes[i:i+NUM_CODES_PER_BUNDLE]
            for i in range(0, len(codes), NUM_CODES_PER_BUNDLE)
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


class PaperQueryBuilder(QueryBuilder):

    def buildQueriesForArgs(self, codes):
        if codes == '':
            logging.warning('No codes provided (get(["..."]) or get("something") Proceeding to fetch all papers on Gallica. Stop me if you wish!')
            return self.buildSRUQueriesForAllRecords()
        if not isinstance(codes, list):
            codes = [codes]
        return self.buildSRUQueriesForCodes(codes)

    def buildSRUQueriesForCodes(self, codes):
        sruQueries = []
        for i in range(0, len(codes), NUM_CODES_PER_BUNDLE):
            codesForQuery = codes[i:i + NUM_CODES_PER_BUNDLE]
            sruQuery = PaperQuery(
                startIndex=0,
                numRecords=NUM_CODES_PER_BUNDLE,
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
        if type(codes) == str:
            codes = [codes]
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

