from gallica.factories.paperQueryFactory import PaperQueryFactory


class PaperSearchFactory:

    def __init__(
            self,
            dbLink,
            parse,
            SRUapi,
    ):
        self.queryMaker = PaperQueryFactory(
            gallicaAPI=SRUapi,
            parse=parse
        )
        self.dbLink = dbLink
        self.parse = parse
        self.SRUapi = SRUapi

    def fetchRecordsForTheseCodes(self, codes):
        queries = self.queryMaker.buildForCodes(codes)
        records = self.fetchRecordsForTheseQueries(queries)
        return records

    #TODO: should this be wrapped into the fetch? Get me records for queries, why do I send raw responses back then parse them?
    #TODO: WRAP FETCH AND PARSE TOGETHER
    def fetchRecordsForTheseQueries(self, queries):
        responses = self.SRUapi.fetchAll(queries)
        return self.parse.papers(responses)