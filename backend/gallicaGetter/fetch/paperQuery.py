from typing import List, Optional


class PaperQuery:
    def __init__(
        self,
        start_index: int,
        num_records: int,
        endpoint: str,
        codes: Optional[List[str]],
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

    # TODO: duplicates code in volumeQuery

    def get_params_for_fetch(self):
        base = {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": self.start_index,
            "maximumRecords": self.num_results,
            "query": self.cql and self.cql or self.build_periodical_cql(),
            "collapsing": self.collapsing and "true" or "false",
        }
        return base

    def build_periodical_cql(self):
        if self.codes and self.codes[0]:
            formatted_codes = [f"{code}_date" for code in self.codes]
            return 'arkPress adj "' + '" or arkPress adj "'.join(formatted_codes) + '"'
        else:
            return 'dc.type all "fascicule" and ocr.quality all "Texte disponible"'
