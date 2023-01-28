from typing import List, Optional

from gallicaGetter.fetch.sruQueryMixin import SRUQueryMixin


class PaperQuery(SRUQueryMixin):
    def __init__(
        self, start_index: int, num_records: int, endpoint: str, codes: Optional[List[str]]
    ):
        self.codes = codes
        self.start_index = start_index
        self.num_results = num_records
        self.endpoint_url = endpoint
        self.collapsing = True
        self.cql = self.build_periodical_cql()

    def make_copy(self, start_index: int, num_records: int):
        return PaperQuery(start_index, num_records, self.endpoint_url, self.codes)

    def __repr__(self):
        return f"PaperQuery({self.codes}, {self.start_index}, {self.num_results})"
