from dataclasses import dataclass
from typing import List, Optional
from gallicaGetter.parse_xml import (
    get_paper_code_from_record_xml,
    get_paper_title_from_record_xml,
    get_records_from_xml,
    get_url_from_record,
)
from gallicaGetter.gallicaWrapper import GallicaWrapper
from gallicaGetter.paperQuery import PaperQuery
from gallicaGetter.base_query_builds import bundle_codes, NUM_CODES_PER_BUNDLE
from gallicaGetter.index_query_builds import build_indexed_queries
import gallicaGetter.wrapperFactory as wF


@dataclass(slots=True)
class PaperRecord:
    code: str
    title: str
    url: str
    publishing_years: List[int]

    @property
    def continuous(self):
        if self.publishing_years:
            return int(self.publishing_years[-1]) - int(
                self.publishing_years[0]
            ) + 1 == len(self.publishing_years)
        else:
            return False


class PapersWrapper(GallicaWrapper):
    """There is no official Gallica endpoint for fetching paper metadata. This class fetches from two Gallica endpoints, SRU (titles, codes) and Issues (publishing years), to get all metadata."""

    def post_init(self):
        self.issues_API = wF.WrapperFactory.issues()

    def get_endpoint_url(self):
        return "https://gallica.bnf.fr/SRU"

    def get(
        self,
        arg_codes: Optional[List[str]] = None,
        stateHooks=None,
        get_all_results: bool = False,
    ) -> List[PaperRecord]:
        if type(arg_codes) == str:
            arg_codes = [arg_codes]

        def build_sru_queries_for_codes() -> List[PaperQuery]:
            """Builds a Gallica query to fetch paper metadata for bundles of code strings"""
            sru_queries = []
            for code_bundle in bundle_codes(arg_codes):
                sru_query = PaperQuery(
                    start_index=0,
                    limit=NUM_CODES_PER_BUNDLE,
                    codes=code_bundle,
                    endpoint_url=self.endpoint_url,
                )
                sru_queries.append(sru_query)
            return sru_queries

        if not arg_codes and get_all_results:
            # Fetch all results, indexing by the number of papers on Gallica. Lengthy fetch.
            queries = build_indexed_queries(
                [PaperQuery(start_index=0, limit=1, endpoint_url=self.endpoint_url)],
                api=self.api,
            )
        elif not arg_codes and not get_all_results:
            raise ValueError(
                "Must provide arg_codes to get specific papers, or set get_all_results=True"
            )
        else:
            if type(arg_codes) == str:
                codes = [arg_codes]
            queries = build_sru_queries_for_codes()
        record_generator = self.get_records_for_queries(queries)
        sru_paper_records = list(record_generator)
        codes = [record.code for record in sru_paper_records]
        year_records = self.issues_API.get(codes)
        years_as_dict = {record.code: record.years for record in year_records}
        for record in sru_paper_records:
            record.publishing_years = years_as_dict[record.code]
        return sru_paper_records

    def parse(self, gallica_responses):
        for response in gallica_responses:
            for record in get_records_from_xml(response.xml):
                yield PaperRecord(
                    code=get_paper_code_from_record_xml(record),
                    title=get_paper_title_from_record_xml(record),
                    url=get_url_from_record(record),
                    publishing_years=[],
                )
