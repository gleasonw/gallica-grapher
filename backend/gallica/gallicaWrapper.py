from gallica.recordGetter import RecordGetter
from gallica.queryBuilder import ParamQueryBuilder
from gallica.params import Params
from gallica.concurrentFetch import ConcurrentFetch
from gallica.parseArkRecord import ParseArkRecord
from gallica.parsePaperRecords import ParsePaperRecords
from gallica.parseOccurrenceRecords import ParseOccurrenceRecords
from gallica.parseGroupedRecordCounts import ParseGroupedRecordCounts


def connect(gallicaAPIselect):
    apiWrappers = {
        'sru': SRUWrapper,
        'issues': IssuesWrapper,
        'contentSearch': ContentWrapper,
    }
    api = gallicaAPIselect.lower()
    if api not in apiWrappers:
        raise ValueError(f'API {api} not supported')
    return apiWrappers[api]()


class GallicaWrapper:
    def __init__(self):
        self.recordGetter = self.buildRecordGetter(
            api=self.buildApi(),
            parser=self.buildParser()
        )
        self.queryBuilder = self.buildQueryBuilder()

    def get(self, grouping, **kwargs):
        raise NotImplementedError

    def buildApi(self):
        raise NotImplementedError

    def buildParser(self):
        raise NotImplementedError

    def buildRecordGetter(self, api, parser):
        return RecordGetter(
            gallicaAPI=api,
            parseData=parser,
        )

    def buildQueryBuilder(self):
        raise NotImplementedError


class SRUWrapper(GallicaWrapper):
    def __init__(self, requestID, ticketID):
        super().__init__()
        self.requestID = requestID
        self.ticketID = ticketID

    def get(self, grouping, **kwargs):
        params = Params(
            terms=kwargs['terms'],
            codes=kwargs['codes'],
            startDate=kwargs['startDate'],
            endDate=kwargs['endDate'],
            link=kwargs['link'],
            grouping=grouping,
            numRecords=kwargs['numRecords'],
            startIndex=kwargs['startIndex'],
        )
        queries = self.queryBuilder.buildQueriesForParams(params)
        return self.recordGetter.getFromQueries(queries=queries)

    def buildApi(self):
        return ConcurrentFetch(baseUrl='https://gallica.bnf.fr/SRU')

    def buildParser(self):
        return ParseOccurrenceRecords(
            requestID=self.requestID,
            ticketID=self.ticketID
        )

    def buildQueryBuilder(self):
        return ParamQueryBuilder()

    def buildRecordGetter(self, api, parser):
        pass


class IssuesWrapper(GallicaWrapper):
    def __init__(self):
        super().__init__()

    def get(self, **kwargs):
        pass


class ContentWrapper(GallicaWrapper):
    def __init__(self):
        super().__init__()

    def get(self, **kwargs):
        pass
