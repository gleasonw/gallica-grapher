from .recordGetter import RecordGetter
from .queryBuilder import OccurrenceQueryBuilder
from .queryBuilder import ContentQueryFactory
from .concurrentFetch import ConcurrentFetch
from .queryBuilder import PaperQueryBuilder
from .parseRecord import buildParser


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

    def buildRecordGetter(self, parser=None):
        return RecordGetter(
            gallicaAPI=self.api,
            parseData=parser or self.buildParser()
        )

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

    def get(self, onUpdateProgress=None, generate=False, queriesWithCounts=None, **kwargs):
        grouping = kwargs.get('grouping')
        if grouping is None:
            grouping = 'year'
            kwargs['grouping'] = grouping
        recordGetter = self.buildRecordGetterForGrouping(grouping)
        recordGenerator = recordGetter.getFromQueries(
            queries=self.buildQueries(kwargs, queriesWithCounts),
            onUpdateProgress=onUpdateProgress
        )
        return recordGenerator if generate else list(recordGenerator)

    def buildRecordGetterForGrouping(self, grouping):
        if grouping == 'all':
            return self.buildRecordGetter(self.soloRecordParser)
        else:
            return self.buildRecordGetter(self.groupedRecordParser)

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
        self.recordGetter = self.buildRecordGetter()

    def get(self, generate=False, **kwargs):
        codes = kwargs.get('codes')
        queries = self.queryBuilder.buildArkQueriesForCodes(codes)
        recordGenerator = self.recordGetter.getFromQueries(queries)
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
        self.recordGetter = self.buildRecordGetter()

    def get(self, ark, term, generate=False):
        query = self.queryBuilder.buildQueryForArkAndTerm(
            ark=ark,
            term=term
        )
        recordGen = self.recordGetter.getFromQueries([query])
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

    def get(self, stateHooks=None, **kwargs):
        SRUrecordGetter = self.buildRecordGetter()
        queries = self.queryBuilder.buildQueriesForArgs(kwargs)
        recordGenerator = SRUrecordGetter.getFromQueries(queries)
        sruPaperRecords = list(recordGenerator)
        codes = [record.code for record in sruPaperRecords]
        issueWrapper = IssuesWrapper()
        yearRecords = issueWrapper.get(codes=codes)
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
    sruWrapper = connect('sru', numWorkers=10)
    records = sruWrapper.get(
        terms='brazza',
        grouping='year',
        generate=True,
        startDate='1900',
        endDate='1910'
    )
    for record in records:
        print(record.getRow())