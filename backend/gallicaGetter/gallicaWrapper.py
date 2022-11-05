from gallicaGetter.queryBuilder import OccurrenceQueryBuilder
from gallicaGetter.queryBuilder import ContentQueryFactory
from gallicaGetter.concurrentFetch import ConcurrentFetch
from gallicaGetter.queryBuilder import PaperQueryBuilder
from gallicaGetter.parseRecord import buildParser


class GallicaWrapper:
    def __init__(self, **kwargs):
        self.api = self.buildAPI(kwargs.get('numWorkers', 10))
        self.parser = None
        self.queryBuilder = self.buildQueryBuilder()
        self.preInit(kwargs)

    def preInit(self, kwargs):
        pass

    def get(self, **kwargs):
        raise NotImplementedError(f'get() not implemented for {self.__class__.__name__}')

    def buildAPI(self, numWorkers):
        raise NotImplementedError(f'buildAPI() not implemented for {self.__class__.__name__}')

    def buildQueryBuilder(self):
        raise NotImplementedError(f'buildQueryBuilder() not implemented for {self.__class__.__name__}')
        
    def getFromQueries(self, queries, parser, onUpdateProgress=None):
        rawResponse = self.api.get(
            queries,
            onUpdateProgress=onUpdateProgress
        )
        records = parser.parseResponsesToRecords(rawResponse)
        return records

    def buildParser(self):
        pass


class SRUWrapper(GallicaWrapper):

    def preInit(self, kwargs):
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

    def get(self, terms, onUpdateProgress=None, generate=False, queriesWithCounts=None, **kwargs):
        grouping = kwargs.get('grouping')
        kwargs['terms'] = terms
        if grouping is None:
            grouping = 'year'
            kwargs['grouping'] = grouping
        recordGenerator = self.getFromQueries(
            queries=self.buildQueries(kwargs, queriesWithCounts),
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

    def buildAPI(self, numWorkers):
        return ConcurrentFetch(
            baseUrl='https://gallica.bnf.fr/SRU',
            numWorkers=numWorkers
        )

    def buildQueryBuilder(self):
        return OccurrenceQueryBuilder(gallicaAPI=self.api)


class IssuesWrapper(GallicaWrapper):

    def preInit(self, kwargs):
        self.parser = self.buildParser()

    def get(self, codes, generate=False):
        queries = self.queryBuilder.buildArkQueriesForCodes(codes)
        recordGenerator = self.getFromQueries(
            queries,
            parser=self.parser
        )
        return recordGenerator if generate else list(recordGenerator)

    def buildParser(self):
        return buildParser('ark')

    def buildAPI(self, numWorkers):
        return ConcurrentFetch(
            'https://gallica.bnf.fr/services/Issues',
            numWorkers=numWorkers
        )

    def buildQueryBuilder(self):
        return PaperQueryBuilder(gallicaAPI=self.api)


class ContentWrapper(GallicaWrapper):

    def preInit(self, kwargs):
        self.parser = buildParser('content')

    def get(self, ark, term, generate=False):
        query = self.queryBuilder.buildQueryForArkAndTerm(
            ark=ark,
            term=term
        )
        recordGen = self.getFromQueries(
            queries=query,
            parser=self.parser
        )
        return recordGen if generate else list(recordGen)

    def buildQueryBuilder(self):
        return ContentQueryFactory()

    def buildParser(self):
        return buildParser('content')

    def buildAPI(self, numWorkers):
        return ConcurrentFetch(
            baseUrl='https://gallica.bnf.fr/services/ContentSearch',
            numWorkers=numWorkers
        )


class PapersWrapper(GallicaWrapper):

    def preInit(self, kwargs):
        self.parser = self.buildParser()
        self.issuesWrapper = IssuesWrapper()

    def get(self, argCodes, stateHooks=None, **kwargs):
        queries = self.queryBuilder.buildQueriesForArgs(argCodes)
        recordGenerator = self.getFromQueries(
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

    def buildAPI(self, numWorkers):
        return ConcurrentFetch(
            baseUrl='https://gallica.bnf.fr/SRU',
            numWorkers=numWorkers
        )

    def buildQueryBuilder(self):
        return PaperQueryBuilder(gallicaAPI=self.api)

    def buildParser(self):
        return buildParser('paper')


if __name__ == '__main__':
    wrapper = IssuesWrapper()
    test = wrapper.get('cb32895690j')
    print(test)