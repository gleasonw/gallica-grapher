import aiohttp.client_exceptions
from gallicaGetter.gallicaWrapper import Response
from gallicaGetter.volumeOccurrence import VolumeOccurrence, VolumeRecord
from gallicaGetter.context import Context, HTMLContext
from typing import Callable, List, Literal, Optional
from pydantic import BaseModel
from functools import partial
from bs4 import BeautifulSoup
import aiohttp

MAX_CONCURRENT_REQUESTS_FOR_CSV = 20


class ContextRow(BaseModel):
    pivot: str
    left_context: str
    right_context: str
    page_url: str
    page: str


class GallicaRecordWithRows(BaseModel):
    paper_title: str
    paper_code: str
    terms: List[str]
    date: str
    url: str
    context: List[ContextRow]


class GallicaRecordWithHTML(BaseModel):
    paper_title: str
    paper_code: str
    terms: List[str]
    date: str
    url: str
    context: HTMLContext


class UserResponse(BaseModel):
    records: List[GallicaRecordWithRows | GallicaRecordWithHTML]
    num_results: int
    origin_urls: List[str]
    est_seconds_to_download: int


def build_html_record(record: VolumeRecord, context: HTMLContext):
    return GallicaRecordWithHTML(
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

        def stringify_and_split(span: BeautifulSoup):
            text = str(span).strip()
            return text.split("(...)")

        i = 0
        while i < len(spans):
            span = spans[i]
            pivot = span.text

            left_context = span.previous_sibling
            if left_context:
                ellipsis_split = stringify_and_split(left_context)
                closest_left_text = ellipsis_split[-1]
            else:
                closest_left_text = ""

            right_context = span.next_sibling
            if right_context:
                ellipsis_split = stringify_and_split(right_context)
                closest_right_text = ellipsis_split[0]

                # check if gallica has made an erroneous (..) split in the middle of our pivot, only for requests with any multi-word terms
                if (
                    any(len(term.split(" ")) > 1 for term in record.terms)
                    and i < len(spans) - 1
                    and closest_right_text == ""
                ):
                    next_pivot = spans[i + 1].text
                    if any(
                        f'"{pivot} {next_pivot}"'.casefold() == term.casefold()
                        for term in record.terms
                    ):
                        pivot = f"{pivot} {next_pivot}"
                        new_right_context = spans[i + 1].next_sibling
                        if new_right_context:
                            ellipsis_split = stringify_and_split(new_right_context)
                            closest_right_text = ellipsis_split[0]

                        # ignore the next span
                        i += 1

            else:
                closest_right_text = ""
            i += 1
            rows.append(
                ContextRow(
                    pivot=pivot,
                    left_context=closest_left_text,
                    right_context=closest_right_text,
                    page_url=f"{record.url}/f{page.page_num}.image.r={pivot}",
                    page=page.page_num,
                )
            )

    return GallicaRecordWithRows(
        paper_title=record.paper_title,
        paper_code=record.paper_code,
        terms=record.terms,
        date=str(record.date),
        url=record.url,
        context=rows,
    )


async def get_context(
    terms: List[str],
    codes: Optional[List[str]] = None,
    year: Optional[int] = 0,
    month: Optional[int] = 0,
    end_year: Optional[int] = 0,
    end_month: Optional[int] = 0,
    day: Optional[int] = 0,
    cursor: Optional[int] = 0,
    limit: Optional[int] = 10,
    link_term: Optional[str] = None,
    link_distance: Optional[int] = 0,
    source: Literal["book", "periodical", "all"] = "all",
    sort: Literal["date", "relevance"] = "relevance",
    parser: Callable[
        [VolumeRecord, HTMLContext], GallicaRecordWithRows | GallicaRecordWithHTML
    ] = build_html_record,
) -> UserResponse:
    """Queries Gallica's SRU and ContentSearch API's to get context for a given term in the archive."""

    link = None
    if link_distance and link_term:
        link_distance = int(link_distance)
        link = (link_term, link_distance)

    total_records = 0
    origin_urls = []
    sru_average_response = 0
    content_average_response = 0

    def set_total_records(num_records: int):
        nonlocal total_records
        total_records = num_records

    def set_origin_urls(urls: List[str]):
        nonlocal origin_urls
        origin_urls = urls

    def update_response_time(current_average: float, new: float):
        if current_average == 0:
            return new
        else:
            return (current_average + new) / 2

    def update_sru_average_response_time(response: Response):
        nonlocal sru_average_response
        sru_average_response = update_response_time(
            sru_average_response, response.elapsed_time
        )

    def update_content_average_response_time(response: Response):
        nonlocal content_average_response
        content_average_response = update_response_time(
            content_average_response, response.elapsed_time
        )

    # get the volumes in which the term appears
    async with aiohttp.ClientSession() as session:
        volume_Gallica_wrapper = VolumeOccurrence()
        gallica_records = await volume_Gallica_wrapper.get(
            terms=terms,
            start_date=make_date_from_year_mon_day(year, month, day),
            end_date=make_date_from_year_mon_day(end_year, end_month, day),
            codes=codes,
            source=source,
            link=link,
            limit=limit,
            start_index=cursor or 0,
            sort=sort,
            on_get_total_records=set_total_records,
            on_get_origin_urls=set_origin_urls,
            on_receive_response=update_sru_average_response_time,
            session=session,
        )

        # get the context for those volumes
        content_wrapper = Context()
        keyed_records = {
            record.url.split("/")[-1]: record for record in gallica_records
        }
        context = await content_wrapper.get(
            [
                (record.url.split("/")[-1], record.terms)
                for _, record in keyed_records.items()
            ],
            session=session,
            on_receive_response=update_content_average_response_time,
        )

        # combine the two
        records_with_context: List[GallicaRecordWithRows | GallicaRecordWithHTML] = []
        for context_response in context:
            corresponding_record = keyed_records[context_response.ark]
            records_with_context.append(parser(corresponding_record, context_response))

        return UserResponse(
            records=records_with_context,
            num_results=total_records,
            origin_urls=origin_urls,
            est_seconds_to_download=int(
                (
                    (total_records / 50) * sru_average_response
                    + total_records * content_average_response
                )
                / MAX_CONCURRENT_REQUESTS_FOR_CSV
            ),
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
