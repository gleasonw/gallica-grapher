from gallicaGetter.build.queryBuilder import OccurrenceQueryBuilder
from gallicaGetter.build.queryBuilder import ContentQueryBuilder
from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from gallicaGetter.build.queryBuilder import PaperQueryBuilder
from gallicaGetter.build.queryBuilder import FullTextQueryBuilder
from gallicaGetter.parse.parseRecord import buildParser
from typing import List


class GallicaWrapper:
    def __init__(self, **kwargs):
        self.api = ConcurrentFetch(numWorkers=kwargs.get('numWorkers', 10))
        self.baseURL = self.getBaseURL()
        self.parser = None
        self.queryBuilder = self.getQueryBuilder()
        self.postInit(kwargs)

    def postInit(self, kwargs):
        pass

    def get(self, **kwargs):
        raise NotImplementedError(f'get() not implemented for {self.__class__.__name__}')

    def getQueryBuilder(self):
        raise NotImplementedError(f'buildQueryBuilder() not implemented for {self.__class__.__name__}')

    def getBaseURL(self):
        raise NotImplementedError(f'getBaseURL() not implemented for {self.__class__.__name__}')
        
    def fetchFromQueries(self, queries, parser, onUpdateProgress=None):
        rawResponse = self.api.get(
            queries,
            onUpdateProgress=onUpdateProgress
        )
        records = parser.parseResponsesToRecords(rawResponse)
        return records

    def buildParser(self):
        pass


class SRUWrapper(GallicaWrapper):

    def postInit(self, kwargs):
        self.groupedRecordParser = buildParser(
            desiredRecord='groupedCount',
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )
        self.soloRecordParser = buildParser(
            desiredRecord='occurrence',
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )

    def getQueryBuilder(self):
        return OccurrenceQueryBuilder(props=self)

    def getBaseURL(self):
        return 'https://gallica.bnf.fr/SRU'

    def get(self, terms, onUpdateProgress=None, generate=False, queriesWithCounts=None, **kwargs) -> List:
        grouping = kwargs.get('grouping')
        kwargs['terms'] = terms
        if grouping is None:
            grouping = 'year'
            kwargs['grouping'] = grouping
        queries = self.buildQueries(
            kwargs,
            queriesWithCounts
        )
        recordGenerator = self.fetchFromQueries(
            queries=queries,
            parser=self.soloRecordParser if grouping == 'all' else self.groupedRecordParser,
            onUpdateProgress=onUpdateProgress
        )
        return recordGenerator if generate else list(recordGenerator)

    def buildQueries(self, kwargs, queriesWithCounts):
        if queriesWithCounts:
            return self.queryBuilder.indexQueriesWithNumResults(queriesWithCounts)
        else:
            return self.queryBuilder.buildQueriesForArgs(kwargs)

    def getNumResultsForArgs(self, args):
        baseQueries = self.queryBuilder.buildBaseQueriesFromArgs(args)
        return self.queryBuilder.getNumResultsForEachQuery(baseQueries)


class IssuesWrapper(GallicaWrapper):

    def postInit(self, kwargs):
        self.parser = buildParser('ark')

    def getQueryBuilder(self):
        return PaperQueryBuilder(props=self)

    def getBaseURL(self):
        return 'https://gallica.bnf.fr/services/Issues'

    def get(self, codes, generate=False):
        queries = self.queryBuilder.buildArkQueriesForCodes(codes)
        recordGenerator = self.fetchFromQueries(
            queries,
            parser=self.parser
        )
        return recordGenerator if generate else list(recordGenerator)


class ContentWrapper(GallicaWrapper):

    def postInit(self, kwargs):
        self.parser = buildParser('content')

    def getQueryBuilder(self):
        return ContentQueryBuilder(props=self)

    def getBaseURL(self):
        return 'https://gallica.bnf.fr/services/ContentSearch'

    def get(self, ark, term, generate=False):
        query = self.queryBuilder.buildQueryForArkAndTerm(
            ark=ark,
            term=term
        )
        recordGen = self.fetchFromQueries(
            queries=query,
            parser=self.parser
        )
        return recordGen if generate else list(recordGen)


class PapersWrapper(GallicaWrapper):

    def postInit(self, kwargs):
        self.parser = buildParser('paper')
        self.issuesWrapper = IssuesWrapper()

    def getQueryBuilder(self):
        return PaperQueryBuilder(props=self)

    def getBaseURL(self):
        return 'https://gallica.bnf.fr/SRU'

    def get(self, argCodes, stateHooks=None, **kwargs):
        queries = self.queryBuilder.buildQueriesForArgs(argCodes)
        recordGenerator = self.fetchFromQueries(
            queries,
            parser=self.parser,
        )
        sruPaperRecords = list(recordGenerator)
        codes = [record.code for record in sruPaperRecords]
        yearRecords = self.issuesWrapper.get(codes)
        yearsAsDict = {record.code: record.years for record in yearRecords}
        for record in sruPaperRecords:
            record.addYearsFromArk(yearsAsDict[record.code])
        return sruPaperRecords

    def getNumResultsForArgs(self, **kwargs):
        pass


class FullTextWrapper(GallicaWrapper):

    def postInit(self, kwargs):
        self.parser = buildParser('fullText')

    def getBaseURL(self):
        return 'https://gallica.bnf.fr'

    def getQueryBuilder(self):
        return FullTextQueryBuilder(props=self)

    def get(self, arkCodes, generate=False):
        queries = self.queryBuilder.buildQueriesForArkCodes(arkCodes)
        recordGen = self.fetchFromQueries(
            queries=queries,
            parser=self.parser
        )
        return recordGen if generate else list(recordGen)

    def buildParser(self):
        return


if __name__ == '__main__':
    wrapper = FullTextWrapper()
    test = wrapper.get(['bpt6k5891662', 'bpt6k5881238'])
    print(test[1].get_ocr_quality())
