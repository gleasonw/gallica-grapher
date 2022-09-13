from cqlFactory import CQLStringForPaperCodes
from query import Query


class PaperQueryFactory:

    def __init__(self):
        self.cql = CQLStringForPaperCodes()

    def buildSRUQueriesForCodes(self, codes):
        cqlStrings = self.cql.build(codes)
        for string in cqlStrings:
            yield Query(
                url=string,
                startIndex=1,
                numRecords=50,
                collapsing=True
            )

    def buildARKQueriesForCodes(self, codes):
        for code in codes:
            yield Query(
                url=f'ark:/12148/{code}/date',
                startIndex=1,
                numRecords=1,
                collapsing=False
            )




