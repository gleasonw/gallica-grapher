from gallica.recordGetter import RecordGetter
from gallica.queryFactory import OccurrenceQueryFactory
from gallica.queryFactory import ContentQueryFactory
from gallica.concurrentFetch import ConcurrentFetch
from gallica.parseArkRecord import ParseArkRecord
from gallica.parsePaperRecords import ParsePaperRecords
from gallica.parseContentRecord import ParseContentRecord
from gallica.parseOccurrenceRecords import ParseOccurrenceRecords
from gallica.parseGroupedRecordCounts import ParseGroupedRecordCounts
from gallica.queryFactory import PaperQueryFactory


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
        self.groupedRecordParser = ParseGroupedRecordCounts(
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )
        self.soloRecordParser = ParseOccurrenceRecords(
            ticketID=kwargs.get('ticketID'),
            requestID=kwargs.get('requestID')
        )

    def get(self, onUpdateProgress=None, generate=False, queriesWithCounts=None, **kwargs):
        grouping = kwargs.get('grouping')
        if grouping is None:
            grouping = 'year'
            kwargs['grouping'] = grouping
        recordGetter = self.buildRecordGetter(
            parser=self.soloRecordParser if grouping == 'all' else self.groupedRecordParser
        )
        queries = self.getQueriesForArgs(
            args=kwargs,
            storedQueries=queriesWithCounts
        )
        recordGenerator = recordGetter.getFromQueries(
            queries=queries,
            onUpdateProgress=onUpdateProgress
        )
        return recordGenerator if generate else list(recordGenerator)

    def getQueriesForArgs(self, args, storedQueries):
        if storedQueries:
            if args['grouping'] == 'all':
                return self.queryBuilder.indexEachQueryFromNumResults(storedQueries)
            else:
                return [query for query, _ in storedQueries]
        else:
            return self.queryBuilder.buildQueriesForArgs(args)

    def getNumRecordsForArgs(self, **kwargs):
        baseQueries = self.queryBuilder.buildQueriesForArgs(kwargs)
        return self.getNumResultsForEachQuery(baseQueries)

    def getNumResultsForEachQuery(self, queries) -> list:
        responses = self.api.get(queries)
        numResultsForQueries = [
            (response.query, self.soloRecordParser.getNumResults(response.xml))
            for response in responses
        ]
        return numResultsForQueries

    def buildAPI(self):
        return ConcurrentFetch(baseUrl='https://gallica.bnf.fr/SRU')

    def buildQueryBuilder(self):
        return OccurrenceQueryFactory(gallicaAPI=self.api)


class IssuesWrapper(GallicaWrapper):

    def preInit(self, kwargs):
        self.recordGetter = self.buildRecordGetter()

    def get(self, generate=False, **kwargs):
        codes = kwargs.get('codes')
        queries = self.queryBuilder.buildArkQueriesForCodes(codes)
        recordGenerator = self.recordGetter.getFromQueries(queries)
        return recordGenerator if generate else list(recordGenerator)

    def buildParser(self):
        return ParseArkRecord()

    def buildAPI(self):
        return ConcurrentFetch('https://gallica.bnf.fr/services/Issues')

    def buildQueryBuilder(self):
        return PaperQueryFactory(gallicaAPI=self.api)


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
        return ParseContentRecord()

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

    def getNumRecordsForArgs(self, **kwargs):
        pass

    def buildAPI(self):
        return ConcurrentFetch(baseUrl='https://gallica.bnf.fr/SRU')

    def buildQueryBuilder(self):
        return PaperQueryFactory(gallicaAPI=self.api)

    def buildParser(self):
        return ParsePaperRecords()