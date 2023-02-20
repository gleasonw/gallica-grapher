import asyncio
from gallicaGetter.volumeOccurrenceWrapper import VolumeOccurrenceWrapper, VolumeRecord
from gallicaGetter.contentWrapper import ContextWrapper, HTMLContext
from typing import Callable, List, Literal, Optional
from pydantic import BaseModel
from functools import partial
from bs4 import BeautifulSoup
import aiohttp


class ContextRow(BaseModel):
    pivot: str
    left_context: str
    right_context: str
    page_url: str


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

        def stringify_and_split(span: BeautifulSoup):
            text = str(span).strip()
            return text.split("(...)")

        for span in spans:
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
            else:
                closest_right_text = ""

            rows.append(
                ContextRow(
                    pivot=pivot,
                    left_context=closest_left_text,
                    right_context=closest_right_text,
                    page_url=f'{record.url}/f{page.page_num}.image.r="{pivot}"',
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
    async with aiohttp.ClientSession() as session:
        volume_Gallica_wrapper = VolumeOccurrenceWrapper()
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
            session=session,
        )

        # get the context for those volumes
        content_wrapper = ContextWrapper()
        keyed_records = {
            record.url.split("/")[-1]: record for record in gallica_records
        }
        context = await content_wrapper.get(
            [
                (record.url.split("/")[-1], record.terms)
                for _, record in keyed_records.items()
            ],
            session=session,
        )

        # combine the two
        records_with_context: List[GallicaRecord] = []
        for context_response in context:
            corresponding_record = keyed_records[context_response.ark]
            records_with_context.append(parser(corresponding_record, context_response))

        return UserResponse(
            records=records_with_context,
            num_results=total_records,
            origin_urls=origin_urls,
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


async def stream_all_records_with_context(
    terms: List[str],
    codes: Optional[List[str]] = None,
    start_year: Optional[int] = 0,
    start_month: Optional[int] = 0,
    end_year: Optional[int] = 0,
    end_month: Optional[int] = 0,
    day: Optional[int] = 0,
    link_term: Optional[str] = None,
    link_distance: Optional[int] = 0,
    source: Literal["book", "periodical", "all"] = "all",
    sort: Literal["date", "relevance"] = "relevance",
):
    """Queries Gallica's SRU and ContentSearch API's to get all context for a given term in the archive; begins a CSV download."""

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

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(40)
        volume_Gallica_wrapper = VolumeOccurrenceWrapper()
        gallica_records = await volume_Gallica_wrapper.get(
            terms=terms,
            start_date=make_date_from_year_mon_day(start_year, start_month, day),
            end_date=make_date_from_year_mon_day(end_year, end_month, day),
            codes=codes,
            source=source,
            link=link,
            sort=sort,
            on_get_total_records=set_total_records,
            on_get_origin_urls=set_origin_urls,
            get_all_results=True,
            session=session,
            semaphore=semaphore,
        )

        # get the context for those volumes
        content_wrapper = ContextWrapper()

        batch_of_num_workers = []
        continue_loop = True

        yield "paper_title\tpaper_code\tdate\turl\tleft_context\tpivot\tright_context\n"

        while continue_loop:
            for _ in range(5):
                try:
                    batch_of_num_workers.append(next(gallica_records))
                except StopIteration:
                    continue_loop = False
                    break
            code_dict = {
                record.url.split("/")[-1]: record for record in batch_of_num_workers
            }
            context = await content_wrapper.get(
                [
                    (record.url.split("/")[-1], record.terms)
                    for record in batch_of_num_workers
                ],
                session=session,
                semaphore=semaphore,
            )
            for context_response in context:
                record = code_dict[context_response.ark]
                row = build_row_record(record, context_response)
                for context_row in row.context:
                    yield f"{row.paper_title}\t{row.paper_code}\t{row.date}\t{row.url}\t{context_row.left_context}\t{context_row.pivot}\t{context_row.right_context}\n"
