from gallicaGetter.volumeOccurrenceWrapper import VolumeRecord
from gallicaGetter.contentWrapper import HTMLContext
from typing import Callable, List, Literal, Optional
from pydantic import BaseModel
from gallicaGetter import wrapperFactory as wF
from functools import partial
from bs4 import BeautifulSoup


class ContextRow(BaseModel):
    pivot: str
    left_context: str
    right_context: str


class GallicaRecord(BaseModel):
    paper_title: str
    paper_code: str
    terms: List[str]
    date: str
    url: str
    context: HTMLContext | List[ContextRow]


class UserResponse(BaseModel):
    records: List[GallicaRecord]
    num_results: int
    origin_urls: List[str]


def build_html_record(record: VolumeRecord, context: HTMLContext):
    return GallicaRecord(
        paper_title=record.paper_title,
        paper_code=record.paper_code,
        terms=record.terms,
        date=str(record.date),
        url=record.url,
        context=context,
    )


def build_row_record(record: VolumeRecord, context: HTMLContext):
    """Split the Gallica HTML context on the highlighted spans, creating rows of pivot (span), left context, and right context."""
    rows: List[ContextRow] = []

    for page in context.pages:
        soup = BeautifulSoup(page.context, "html.parser")
        spans = soup.find_all("span", {"class": "highlight"})
        for span in spans:
            pivot = span.text
            left_context = span.previous_sibling
            if left_context:
                left_context = str(left_context).strip()
            else:
                left_context = ""
            right_context = span.next_sibling
            if right_context:
                right_context = str(right_context).strip()
            else:
                right_context = ""
            rows.append(
                ContextRow(
                    pivot=pivot,
                    left_context=left_context,
                    right_context=right_context,
                )
            )

    return GallicaRecord(
        paper_title=record.paper_title,
        paper_code=record.paper_code,
        terms=record.terms,
        date=str(record.date),
        url=record.url,
        context=rows,
    )


def get_context(
    terms: List[str],
    codes: Optional[List[str]] = None,
    year: Optional[int] = 0,
    month: Optional[int] = 0,
    day: Optional[int] = 0,
    cursor: Optional[int] = 0,
    limit: Optional[int] = 10,
    link_term: Optional[str] = None,
    link_distance: Optional[int] = 0,
    source: Literal["book", "periodical", "all"] = "all",
    sort: Literal["date", "relevance"] = "relevance",
    parser: Callable[[VolumeRecord, HTMLContext], GallicaRecord] = build_html_record,
) -> UserResponse:
    """Queries Gallica's SRU and ContentSearch API's to get context for a given term in the archive."""

    link = None
    if link_distance and link_term:
        link_distance = int(link_distance)
        link = (link_term, link_distance)

    total_records = 0
    origin_urls = []

    def set_total_records(num_records: int):
        nonlocal total_records
        total_records = num_records

    def set_origin_urls(urls: List[str]):
        nonlocal origin_urls
        origin_urls = urls

    # get the volumes in which the term appears
    volume_Gallica_wrapper = wF.WrapperFactory.volume()
    gallica_records = volume_Gallica_wrapper.get(
        terms=terms,
        start_date=make_date_from_year_mon_day(year, month, day),
        codes=codes,
        source=source,
        link=link,
        num_results=limit,
        start_index=cursor or 0,
        sort=sort,
        on_get_total_records=set_total_records,
        on_get_origin_urls=set_origin_urls,
    )

    # get the context for those volumes
    content_wrapper = wF.WrapperFactory.context()
    keyed_records = {record.url.split("/")[-1]: record for record in gallica_records}
    context = content_wrapper.get(
        [
            (record.url.split("/")[-1], record.terms)
            for _, record in keyed_records.items()
        ]
    )

    # combine the two
    records_with_context: List[GallicaRecord] = []
    for context_response in context:
        corresponding_record = keyed_records[context_response.ark]
        records_with_context.append(parser(corresponding_record, context_response))

    return UserResponse(
        records=records_with_context, num_results=total_records, origin_urls=origin_urls
    )


get_html_context = partial(get_context, parser=build_html_record)

get_row_context = partial(get_context, parser=build_row_record)


def make_date_from_year_mon_day(
    year: Optional[int], month: Optional[int], day: Optional[int]
) -> str:
    if year and month and day:
        return f"{year}-{month}-{day}"
    elif month:
        return f"{year}-{month}"
    elif year:
        return f"{year}"
    else:
        return ""
