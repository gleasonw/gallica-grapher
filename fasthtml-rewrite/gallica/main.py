import asyncio
from io import StringIO
import time
import aiohttp.client_exceptions
from bs4 import BeautifulSoup, ResultSet
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple
from gallica.context import Context, HTMLContext
from gallica.contextSnippets import (
    ContextSnippetQuery,
    ContextSnippets,
    ExtractRoot,
)
from gallica.mostFrequent import get_gallica_core
from gallica.imageSnippet import ImageQuery, ImageResponse, ImageSnippet
import aiohttp
from gallica.queries import ContentQuery
from gallica.mostFrequent import get_sample_text
from gallica.volumeOccurrence import VolumeOccurrence, VolumeRecord
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from fasthtml.common import Div

from gallica.models import (
    ContextRow,
    ContextSearchArgs,
    GallicaPageContext,
    GallicaRowContext,
    OccurrenceArgs,
    TopCity,
    TopPaper,
)


MAX_PAPERS_TO_SEARCH = 600


# limit number of requests for routes... top_paper is more intensive


async def date_params(
    year: Optional[int] = 0,
    month: Optional[int] = 0,
    end_year: Optional[int] = 0,
    end_month: Optional[int] = 0,
):
    return {
        "start_date": make_date_from_year_mon_day(year=year, month=month),
        "end_date": make_date_from_year_mon_day(year=end_year, month=end_month),
    }


top_paper_lock = asyncio.Lock()


def get_lock():
    return top_paper_lock


class TopResponse(BaseModel):
    top_papers: List[TopPaper]
    top_cities: List[TopCity]


async def image_snippet(ark: str, term: str, page: int) -> ImageResponse | None:
    async with aiohttp.ClientSession() as session:
        images = [
            image
            async for image in ImageSnippet.get(
                queries=[ImageQuery(ark=ark, page=page, term=term)], session=session
            )
        ]
        if images is None or len(images) == 0:
            return None
        image = images[0]
        return ImageResponse(
            image=image.image,
            ark=image.ark,
            page=image.page,
            term=image.term,
        )


async def most_terms_at_time(
    term: str,
    year: int,
    month: int | None = None,
    max_n: int = 1,
    sample_size: int = 50,
) -> List[Tuple[str, int]]:
    async with aiohttp.ClientSession() as session:
        counts = await get_gallica_core(
            root_gram=term,
            max_n=max_n,
            start_date=make_date_from_year_mon_day(year=year, month=month),
            session=session,
            sample_size=sample_size,
        )
        return sorted(
            [(term, count) for term, count in counts.items()],
            key=lambda x: x[1],
            reverse=True,
        )[0:20]


class SRUResponse(BaseModel):
    records: List[VolumeRecord]
    total_records: int
    origin_urls: List[str]


async def sru_params(
    terms: List[str],
    codes: Optional[List[str]],
    cursor: Optional[int] = 0,
    limit: Optional[int] = 10,
    date: dict | None = None,
    link_term: Optional[str] = None,
    link_distance: Optional[int] = 0,
    source: Literal["book", "periodical", "all"] = "all",
    sort: Literal["date", "relevance"] = "relevance",
):
    if date is None:
        date = await date_params()
    return ContextSearchArgs(
        start_date=date["start_date"],
        end_date=date["end_date"],
        terms=terms,
        codes=codes,
        cursor=cursor,
        limit=limit,
        link_term=link_term,
        link_distance=link_distance,
        source=source,
        sort=sort,
    )


class RowRecordResponse(BaseModel):
    records: List[GallicaRowContext]
    num_results: int
    origin_urls: List[str]


async def sample(
    term: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    async with aiohttp.ClientSession() as session:
        sample_text = await get_sample_text(
            sample_size=50,
            args=OccurrenceArgs(
                terms=[term],
                start_date=start_date,
                end_date=end_date,
            ),
            session=session,
        )
        if sample_text is None:
            return None
        return sample_text.read()


async def fetch_records_from_gallica(
    args: ContextSearchArgs,
    all_context: Optional[bool] = False,
) -> RowRecordResponse | None:
    async with aiohttp.ClientSession() as session:
        if args.limit and args.limit > 50:
            return None

        try:
            total_records = 0
            origin_urls = []

            def set_total_records(num_records: int):
                nonlocal total_records
                total_records = num_records

            def set_origin_urls(urls: List[str]):
                nonlocal origin_urls
                origin_urls = urls

            keyed_docs = {
                record.ark: record
                for record in await get_documents_with_occurrences(
                    args=args,
                    on_get_total_records=set_total_records,
                    on_get_origin_urls=set_origin_urls,
                    session=session,
                )
            }

            props = {
                "session": session,
                "keyed_docs": keyed_docs,
            }

            if all_context:
                records = [
                    record
                    async for record in get_context_parse_by_row(
                        **props,
                        context_source=get_all_context_in_documents,
                        row_splitter=build_row_record_from_ContentSearch_response,
                    )
                ]
            else:
                records = [
                    record async for record in get_sample_context_by_row(**props)
                ]
            return RowRecordResponse(
                records=records,
                num_results=total_records,
                origin_urls=origin_urls,
            )

        except (
            aiohttp.client_exceptions.ClientConnectorError,
            aiohttp.client_exceptions.ClientConnectionError,
        ):
            return None


async def get_documents_with_occurrences(
    args: ContextSearchArgs,
    on_get_total_records: Callable[[int], None],
    on_get_origin_urls: Callable[[List[str]], None],
    session: aiohttp.ClientSession,
) -> List[VolumeRecord]:
    """Queries Gallica's SRU API to get metadata for a given term in the archive."""

    # get the volumes in which the term appears
    volume_Gallica_wrapper = VolumeOccurrence()
    gallica_records = await volume_Gallica_wrapper.get(
        args=OccurrenceArgs(
            terms=args.terms,
            start_date=args.start_date,
            end_date=args.end_date,
            codes=args.codes,
            source=args.source,
            link_distance=args.link_distance,
            link_term=args.link_term,
            limit=args.limit,
            start_index=args.cursor or 0,
            sort=args.sort,
        ),
        on_get_total_records=on_get_total_records,
        on_get_origin_urls=on_get_origin_urls,
        session=session,
    )

    return list(gallica_records)


def get_sample_context_by_row(
    keyed_docs: Dict[str, VolumeRecord],
    session: aiohttp.ClientSession,
):
    return get_context_parse_by_row(
        session=session,
        keyed_docs=keyed_docs,
        context_source=get_sample_context_in_documents,
        row_splitter=parse_rows_from_sample_context,
    )


async def get_context_parse_by_row(
    keyed_docs: Dict[str, VolumeRecord],
    session: aiohttp.ClientSession,
    context_source: Callable,
    row_splitter: Callable,
):
    for context_response in await context_source(list(keyed_docs.values()), session):
        record = keyed_docs[context_response.ark]
        page_rows = row_splitter(record, context_response)
        yield GallicaRowContext(**record.dict(), context=[row for row in page_rows])


async def get_raw_context(
    keyed_docs: Dict[str, VolumeRecord],
    session: aiohttp.ClientSession,
    context_source: Callable,
):
    for context_response in await context_source(
        records=list(keyed_docs.values()), session=session
    ):
        record = keyed_docs[context_response.ark]
        yield GallicaPageContext(**record.dict(), context=context_response)


def parse_spans_to_rows(spans: ResultSet[Any], terms: List[str]):
    """Gallica returns a blob of context for each page, this function splits the blob into a row for each occurrence."""
    rows: List[ContextRow] = []

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
                any(len(term.split(" ")) > 1 for term in terms)
                and i < len(spans) - 1
                and closest_right_text == ""
            ):
                next_pivot = spans[i + 1].text
                if any(
                    f'"{pivot} {next_pivot}"'.casefold() == term.casefold()
                    for term in terms
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
            )
        )
    return rows


def build_row_record_from_ContentSearch_response(
    record: VolumeRecord, context: HTMLContext
):
    for page in context.pages:
        soup = BeautifulSoup(page.context, "html.parser")
        spans = soup.find_all("span", {"class": "highlight"})
        if spans:
            page_rows = parse_spans_to_rows(
                spans=spans,
                terms=record.terms,
            )
            for row in page_rows:
                row.page_url = f"{record.url}/f{page.page_num}.image.r={row.pivot}"
                row.page_num = page.page_num
                yield row


def parse_rows_from_sample_context(record: VolumeRecord, extract: ExtractRoot):
    """Split the Gallica HTML context on the highlighted spans, creating rows of pivot (span), left context, and right context."""
    # last element is a label, not a context extract
    snippets = extract.fragment.contenu[:-1]

    for snippet in snippets:
        text = snippet.value.contenu
        soup = BeautifulSoup(text, "html.parser")
        spans = soup.find_all("mark")
        if spans:
            page_rows = parse_spans_to_rows(spans, terms=record.terms)
            for row in page_rows:
                row.page_url = snippet.value.url
                row.page_num = snippet.value.page_num
                yield row


async def get_all_context_in_documents(
    records: List[VolumeRecord],
    session: aiohttp.ClientSession,
) -> List[HTMLContext]:
    """Queries Gallica's ContentSearch API's to get context for ALL occurrences within a list of documents."""

    return [
        context
        async for context in Context.get(
            queries=[
                ContentQuery(ark=record.ark, terms=record.terms) for record in records
            ],
            session=session,
        )
    ]


async def get_sample_context_in_documents(
    records: List[VolumeRecord],
    session: aiohttp.ClientSession,
) -> List[ExtractRoot]:
    """Queries Gallica's search result API to show a sample of context instead of the entire batch."""

    # warn if terms length is greater than 1
    if any(len(record.terms) > 1 for record in records):
        print(
            "Warning: using sample context for multi-word terms; only the first term will be used."
        )
    return [
        context
        async for context in ContextSnippets.get(
            queries=[
                ContextSnippetQuery(ark=record.ark, term=record.terms[0])
                for record in records
            ],
            session=session,
        )
    ]


def make_date_from_year_mon_day(
    year: Optional[int], month: Optional[int], day: Optional[int] | None = None
) -> str:
    if year and month and day:
        return f"{year}-{month}-{day}"
    elif month:
        return f"{year}-{month}"
    elif year:
        return f"{year}"
    else:
        return ""


class Series(BaseModel):
    data: List[Tuple[int, float]]
    name: str


series_cache: Dict[str, Series] = {}


async def get(
    term: str,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    grouping: Literal["mois", "annee"] = "mois",
    source: Literal["livres", "presse", "lemonde"] = "presse",
    link_term: Optional[str] = None,
) -> Series:
    key = f"{term}-{start_date}-{end_date}-{grouping}-{source}-{link_term}"
    if key in series_cache:
        return series_cache[key]
    debut = start_date or 1789
    fin = end_date or 1950
    if link_term:
        series_dataframe = await fetch_series_dataframe(
            "https://shiny.ens-paris-saclay.fr/guni/contain",
            {
                "corpus": source,
                "mot1": term.lower(),
                "mot2": link_term.lower(),
                "from": debut,
                "to": fin,
            },
        )
    else:
        series_dataframe = await fetch_series_dataframe(
            "https://shiny.ens-paris-saclay.fr/guni/query",
            {
                "corpus": source,
                "mot": term.lower(),
                "from": debut,
                "to": fin,
            },
        )

    if grouping == "mois" and source != "livres":
        series_dataframe = (
            series_dataframe.groupby(["annee", "mois", "gram"])
            .agg({"n": "sum", "total": "sum"})
            .reset_index()
        )
    if grouping == "annee":
        series_dataframe = (
            series_dataframe.groupby(["annee", "gram"])
            .agg({"n": "sum", "total": "sum"})
            .reset_index()
        )

    def calc_ratio(row):
        if row.total == 0:
            return 0
        return row.n / row.total

    series_dataframe["ratio"] = series_dataframe.apply(
        lambda row: calc_ratio(row), axis=1
    )
    if all(series_dataframe.ratio == 0):
        raise Exception("No records found")

    def get_unix_timestamp(row) -> int:
        year = int(row.get("annee", 0))
        month = int(row.get("mois", 1))

        dt = datetime(year, month, 1)
        return int(dt.timestamp() * 1000)

    data = series_dataframe.apply(
        lambda row: (get_unix_timestamp(row), row["ratio"]), axis=1
    ).tolist()

    series = Series(
        data=data,
        name=term,
    )
    series_cache[key] = series
    return series


async def fetch_series_dataframe(url: str, params: Dict):
    async with aiohttp.ClientSession() as session:
        start = time.time()
        async with session.get(url, params=params) as response:
            print(f"Fetched {response.url}")
            print(f"Took {time.time() - start} seconds")
            if response.status != 200:
                raise Exception("Could not connect to Gallicagram! Egads!")
            return pd.read_csv(StringIO(await response.text()))
