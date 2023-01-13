from typing import List, Optional

from pydantic import BaseModel


class OccurrenceQuery(BaseModel):
    term: str
    start_date: str
    end_date: str
    endpoint_url: str
    start_index: int
    num_records: int
    codes: Optional[List[str]] = None
    num_results: int = 0
    link_term: Optional[str] = ""
    link_distance: Optional[int] = 0
    collapsing = False

    def make_copy(self, start_index: int, num_records: int = 1):
        return OccurrenceQuery(
            term=self.term,
            codes=self.codes,
            start_date=self.start_date,
            end_date=self.end_date,
            endpoint_url=self.endpoint_url,
            start_index=start_index,
            num_records=num_records,
            link_term=self.link_term,
            link_distance=self.link_distance,
        )

    def generate_cql(self):
        cql_components = []
        (termCQL := self.build_gram_cql()) and cql_components.append(termCQL)
        (dateCQL := self.build_date_cql()) and cql_components.append(dateCQL)
        (paperCQL := self.build_periodical_cql()) and cql_components.append(paperCQL)
        return " and ".join(cql_components)

    def build_date_cql(self):
        if self.start_date and self.end_date:
            return f'gallicapublication_date>="{self.start_date}" and gallicapublication_date<"{self.end_date}"'
        elif self.start_date:
            return f'gallicapublication_date="{self.start_date}"'
        else:
            return ""

    def build_gram_cql(self) -> str:
        if self.link_term:
            return f'text adj "{self.term}" prox/unit=word/distance={self.link_distance} "{self.link_term}"'
        elif self.term:
            return f'text adj "{self.term}"'
        else:
            return ""

    def get_params_for_fetch(self):
        base = {
            "operation": "searchRetrieve",
            "exactSearch": "True",
            "version": 1.2,
            "startRecord": self.start_index,
            "maximumRecords": self.num_records,
            "query": self.generate_cql(),
            "collapsing": self.collapsing and "true" or "false",
        }
        return base

    def build_periodical_cql(self):
        if self.codes and self.codes[0]:
            formatted_codes = [f"{code}_date" for code in self.codes]
            return 'arkPress adj "' + '" or arkPress adj "'.join(formatted_codes) + '"'
        else:
            return 'dc.type all "fascicule" and ocr.quality all "Texte disponible"'

    def __repr__(self):
        return f"Occurrence Query ({self.cql})"
