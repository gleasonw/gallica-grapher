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
        'papers' : PapersWrapper,
    }
    api = gallicaAPIselect.lower()
    if api not in apiWrappers:
        raise ValueError(f'API {api} not supported')
    return apiWrappers[api](**kwargs)


class GallicaWrapper:
    def __init__(self, **kwargs):
        self.preInit(kwargs)

    def preInit(self, kwargs):
        pass

    def buildRecordGetter(self, api, parser):
        return RecordGetter(
            gallicaAPI=api,
            parseData=parser,
        )


class SRUWrapper(GallicaWrapper):

    def preInit(self, kwargs):
        self.requestID = kwargs.get('requestID')
        self.ticketID = kwargs.get('ticketID')

    def get(self, generate=False, grouping='year', **kwargs):
        parser = self.buildParserForGrouping(grouping)
        api = self.buildApi()
        recordGetter = self.buildRecordGetter(
            api=api,
            parser=parser
        )
        queryBuilder = self.buildQueryBuilder(
            api=api,
            parser=parser
        )
        queries = queryBuilder.buildQueriesForArgs(kwargs)
        recordGenerator = recordGetter.getFromQueries(queries=queries)
        return recordGenerator if generate else list(recordGenerator)

    def buildApi(self):
        return ConcurrentFetch(baseUrl='https://gallica.bnf.fr/SRU')

    def buildParserForGrouping(self, grouping):
        if grouping == 'all':
            return ParseOccurrenceRecords(
                ticketID=self.ticketID,
                requestID=self.requestID
            )
        else:
            return ParseGroupedRecordCounts(
                ticketID=self.ticketID,
                requestID=self.requestID
            )

    def buildQueryBuilder(self, api, parser):
        return OccurrenceQueryFactory(
            gallicaAPI=api,
            parse=parser,
        )


class IssuesWrapper(GallicaWrapper):

    def preInit(self, kwargs):
        api = self.buildAPI()
        parser = self.buildParser()
        self.recordGetter = self.buildRecordGetter(
            api=api,
            parser=parser
        )
        self.queryBuilder = self.buildQueryBuilder(
            api=api,
            parser=parser
        )

    def get(self, generate=False, **kwargs):
        codes = kwargs.get('codes')
        queries = self.queryBuilder.buildArkQueriesForCodes(codes)
        recordGenerator = self.recordGetter.getFromQueries(queries)
        return recordGenerator if generate else list(recordGenerator)

    def buildParser(self):
        return ParseArkRecord()

    def buildAPI(self):
        return ConcurrentFetch('https://gallica.bnf.fr/services/Issues')

    def buildQueryBuilder(self, api, parser):
        return PaperQueryFactory(
            gallicaAPI=api,
            parse=parser,
        )


class ContentWrapper(GallicaWrapper):

    def preInit(self, kwargs):
        self.queryBuilder = self.buildQueryBuilder()
        self.recordGetter = self.buildRecordGetter(
            api=self.buildAPI(),
            parser=self.buildParser()
        )

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

    #TODO: rewrite to get ark queries and compose, just copy previous code essentially
    def getPapers(self, generate=False, **kwargs):
        api = self.buildApi()
        parser = ParsePaperRecords()
        recordGetter = self.buildRecordGetter(
            api=api,
            parser=parser
        )
        queryBuilder = PaperQueryFactory(
            gallicaAPI=api,
            parse=parser,
        )
        queries = queryBuilder.buildQueriesForArgs(kwargs)
        recordGenerator = recordGetter.getFromQueries(queries=queries)
        return recordGenerator if generate else list(recordGenerator)

    def buildApi(self):
        return ConcurrentFetch(baseUrl='https://gallica.bnf.fr/SRU')


if __name__ == '__main__':
    testWrap = connect('sru')
    records = testWrap.getPapers(codes=['cb32895690j'])
    print(records)