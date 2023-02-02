from typing import List, Optional
from dataclasses import dataclass


@dataclass(slots=True)
class PaperQuery:
    """Struct for a paper metadata query to Gallica's SRU API. Similar to VolumeQuery, but with fewer params and a different CQL build."""

    start_index: int
    limit: int
    endpoint_url: str
    codes: Optional[List[str]] = None
    cql: Optional[str] = None
    gallica_results_for_params: int = 0

    def __post_init__(self):
        if self.codes and self.codes[0]:
            formatted_codes = [f"{code}_date" for code in self.codes]
            self.cql = (
                'arkPress adj "' + '" or arkPress adj "'.join(formatted_codes) + '"'
            )
        else:
            self.cql = 'dc.type all "fascicule" and ocr.quality all "Texte disponible"'

    def make_copy(self, start_index: int, num_records: int):
        return PaperQuery(start_index, num_records, self.endpoint_url, self.codes)

    def get_params_for_fetch(self):
        base = {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": self.start_index,
            "maximumRecords": self.limit,
            "query": self.cql,
            "collapsing": "true",
        }
        return base
