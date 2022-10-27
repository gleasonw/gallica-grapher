from gallica.recordGetter import RecordGetter
from gallica.queryBuilder import OccurrenceQueryBuilder
from gallica.queryBuilder import ContentQueryFactory
from gallica.concurrentFetch import ConcurrentFetch
from gallica.queryBuilder import PaperQueryBuilder
import parseRecord


def connect(gallicaAPIselect, **kwargs):
    apiWrappers = {
        'sru': SRUWrapper,
        'issues': IssuesWrapper,
        'content': ContentWrapper,
        'papers': PapersWrapper,
    }
    api = gallicaAPIselect.lower()
    if api not in apiWrappers:
        raise ValueError(f'API {api} not supported')
    return apiWrappers[api](**kwargs)


class GallicaWrapper:
    def __init__(self, **kwargs):
        self.api = self.buildAPI()
        self.parser = None
        self.queryBuilder = self.buildQueryBuilder()
        self.preInit(kwargs)

    def preInit(self, kwargs):
        pass

    def buildAPI(self):
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
        self.groupedRecordParser = parseRecord.build(
            desiredRecord='groupedCount',
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )
        self.soloRecordParser = parseRecord.build(
            desiredRecord='occurrence',
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )

    #TODO: refactor... this method includes too many special cases (3)
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

    def buildAPI(self):
        return ConcurrentFetch(baseUrl='https://gallica.bnf.fr/SRU')

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
        return parseRecord.build('paper')

    def buildAPI(self):
        return ConcurrentFetch('https://gallica.bnf.fr/services/Issues')

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
        return parseRecord.build('content')

    def buildAPI(self):
        return ConcurrentFetch('https://gallica.bnf.fr/services/ContentSearch')


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

    def buildAPI(self):
        return ConcurrentFetch(baseUrl='https://gallica.bnf.fr/SRU')

    def buildQueryBuilder(self):
        return PaperQueryBuilder(gallicaAPI=self.api)

    def buildParser(self):
        return ParsePaperRecords()