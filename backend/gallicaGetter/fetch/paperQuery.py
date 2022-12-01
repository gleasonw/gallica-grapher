from typing import List

from gallicaGetter.fetch.sruQueryMixin import SRUQueryMixin


class PaperQuery(SRUQueryMixin):

    def __init__(self, start_index: int, num_records: int,
                 endpoint: str, codes: List[str] = None):
        self.codes = codes
        self.startIndex = start_index
        self.numRecords = num_records
        self.endpoint = endpoint
        self.collapsing = True
        self.cql = self.build_periodical_cql()

    def make_copy(self, start_index: int, num_records: int):
        return PaperQuery(start_index, num_records, self.endpoint, self.codes)

    def __repr__(self):
        return f'PaperQuery({self.codes}, {self.startIndex}, {self.numRecords})'
