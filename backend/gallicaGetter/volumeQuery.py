from typing import List, Literal, Optional, Tuple
from pydantic import BaseModel


class VolumeQuery(BaseModel):
    """Struct for a query to Gallica's SRU API."""
    term: str
    start_date: Optional[str]
    end_date: Optional[str]
    endpoint_url: str
    start_index: int
    limit: int
    link: Optional[Tuple[str, int]] = None
    source: Optional[Literal["book", "periodical", "all"]] = "all"
    codes: Optional[List[str]] = None
    sort: Optional[Literal["date", "relevance"]] = None
    gallica_results_for_params: int = 0
    collapsing = False

    def make_copy(self, start_index: int, num_records: int = 1):
        return VolumeQuery(
            term=self.term,
            codes=self.codes,
            start_date=self.start_date,
            end_date=self.end_date,
            endpoint_url=self.endpoint_url,
            start_index=start_index,
            limit=num_records,
            link=self.link,
            source=self.source,
            sort=self.sort,
        )

    def build_cql_string(self):
        cql_components = []
        if termCQL := self.build_gram_cql():
            cql_components.append(termCQL)
        if dateCQL := self.build_date_cql():
            cql_components.append(dateCQL)
        if paperCQL := self.build_source_sql():
            cql_components.append(paperCQL)
        cql = " and ".join(cql_components)
        if self.sort == "date":
            cql += " sortby dc.date/sort.ascending"
        return cql

    def build_date_cql(self):
        if self.start_date and self.end_date:
            return f'gallicapublication_date>="{self.start_date}" and gallicapublication_date<"{self.end_date}"'
        elif self.start_date:
            return f'gallicapublication_date="{self.start_date}"'
        else:
            return ""

    def build_gram_cql(self) -> str:
        if self.link:
            return f'text adj "{self.term}" prox/unit=word/distance={self.link[1]} "{self.link[0]}"'
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
            "maximumRecords": self.limit,
            "query": self.build_cql_string(),
            "collapsing": self.collapsing and "true" or "false",
        }
        return base

    def build_source_sql(self):
        if self.codes and self.codes[0]:
            formatted_codes = [f"{code}_date" for code in self.codes]
            return 'arkPress adj "' + '" or arkPress adj "'.join(formatted_codes) + '"'
        elif self.source == "periodical":
            base = 'dc.type all "fascicule"'
        elif self.source == "book":
            base = 'dc.type all "monographie"'
        else:
            base = 'dc.type all "fascicule" or dc.type all "monographie"'
        return base + ' and ocr.quality all "Texte disponible"'

    def __repr__(self):
        return f"Volume Query ({self.term})"
