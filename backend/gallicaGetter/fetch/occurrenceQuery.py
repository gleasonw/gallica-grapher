from typing import List
from gallicaGetter.fetch.sruQueryMixin import SRUQueryMixin


class OccurrenceQuery(SRUQueryMixin):

    def __init__(self, term: str, codes: List[str],
                 start_date: str, end_date: str,
                 endpoint: str, start_index: int,
                 num_records: int, link_term: str = None,
                 link_distance: int = 0):
        self.start_date = start_date
        self.end_date = end_date
        self.term = term
        self.codes = codes
        self.link_distance = link_distance
        self.link_term = link_term
        self.cql = self.generate_cql()
        self.start_index = start_index
        self.num_records = num_records
        self.endpoint = endpoint
        self.collapsing = False

    def get_cql_params(self):
        return {
            "term": self.term,
            "endDate": self.end_date,
            "startDate": self.start_date,
            "codes": self.codes,
        }

    def get_start_date(self):
        return self.start_date

    def generate_cql(self):
        cql_components = []
        (termCQL := self.build_gram_cql()) and cql_components.append(termCQL)
        (dateCQL := self.build_date_cql()) and cql_components.append(dateCQL)
        (paperCQL := self.build_periodical_cql()) and cql_components.append(paperCQL)
        return ' and '.join(cql_components)

    def build_date_cql(self):
        if self.start_date and self.end_date:
            return f'gallicapublication_date>="{self.start_date}" and gallicapublication_date<"{self.end_date}"'
        elif self.start_date:
            return f'gallicapublication_date="{self.start_date}"'
        else:
            return ''

    def build_gram_cql(self) -> str:
        if self.link_term:
            return f'text adj "{self.term}" prox/unit=word/distance={self.link_distance} "{self.link_term}"'
        elif self.term:
            return f'text adj "{self.term}"'
        else:
            return ''

    def __repr__(self):
        return f"Query({self.cql})"
