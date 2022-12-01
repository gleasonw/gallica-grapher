from typing import List

from gallicaGetter.fetch.sruQueryMixin import SRUQueryMixin


class PaperQuery(SRUQueryMixin):

    def __init__(self, codes: List[str], startIndex: int,
                 numRecords: int, endpoint: str):
        self.codes = codes
        self.startIndex = startIndex
        self.numRecords = numRecords
        self.endpoint = endpoint
        self.collapsing = True

    def generate_cql(self):
        return self.build_periodical_cql()

    def get_cql_params(self):
        return {"codes": self.codes}

    def __repr__(self):
        return f'PaperQuery({self.codes}, {self.startIndex}, {self.numRecords})'
