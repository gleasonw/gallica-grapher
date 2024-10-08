import asyncio
import aiohttp
import pytest
from gallica.pagination import Pagination
from gallica.context import Context
from gallica.issues import Issues
from gallica.papers import Papers
from gallica.queries import ContentQuery

from gallica.volumeOccurrence import VolumeOccurrence
from gallica.periodOccurrence import PeriodOccurrence
from gallica.pageText import PageQuery, PageText
from gallica.models import OccurrenceArgs

# TODO: add test for malformed query. do we fail gracefully?


@pytest.mark.asyncio
async def test_pagination():
    async with aiohttp.ClientSession() as session:
        pagination = await Pagination.get("bpt6k607811b", session=session)
        assert pagination
        assert pagination.ark == "bpt6k607811b"
        assert pagination.page_count == 4
        assert pagination.has_content is True
        assert pagination.has_toc == False


@pytest.mark.asyncio
async def test_get_page():
    async with aiohttp.ClientSession() as session:
        records = PageText.get(
            page_queries=[PageQuery(ark="bpt6k607811b", page_num=1)], session=session
        )
        list_records = [record async for record in records]
        assert len(list_records) == 1
        first_record = list_records[0]
        assert first_record.ark == "bpt6k607811b"
        assert first_record.page_num == 1
        assert isinstance(first_record.text, str)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("input", "expected_length"),
    [
        ({"terms": ["seattle"], "codes": ["cb32895690j"]}, 268),
        (
            {
                "terms": ["bon pain"],
                "start_date": "1890-01-02",
                "end_date": "1890-01-03",
            },
            1,
        ),
        ({"terms": ["vote des femmes"], "start_date": "1848", "end_date": "1848"}, 2),
        # too many quotes
        (
            {
                "terms": ['""vote des femmes""'],
                "start_date": "1848",
                "end_date": "1848",
            },
            0,
        ),
    ],
)
async def test_get_volume_occurrences(input, expected_length):
    async with asyncio.timeout(10):
        records = await VolumeOccurrence.get(
            OccurrenceArgs(**input), get_all_results=True
        )
    list_records = list(records)
    assert len(list_records) == expected_length


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("input", "expected_length"),
    [
        (
            {
                "terms": ["bon pain"],
                "start_date": "1890",
                "end_date": "1895",
                "grouping": "year",
            },
            6,
        ),
        (
            {
                "terms": ["bon pain"],
                "start_date": "1890",
                "end_date": "1890",
                "grouping": "month",
            },
            12,
        ),
    ],
)
async def test_get_period_occurrences(input, expected_length):
    async with aiohttp.ClientSession() as session:
        records = PeriodOccurrence.get(
            OccurrenceArgs(**input), grouping=input["grouping"], session=session
        )
        list_records = [record async for record in records]
        assert len(list_records) == expected_length


@pytest.mark.asyncio
async def test_get_issues():
    async with aiohttp.ClientSession() as session:
        records = Issues.get("cb344484501", session=session)
        list_records = [record async for record in records]
        assert len(list_records) == 1
        issue = list_records[0]
        assert issue.code == "cb344484501"


@pytest.mark.asyncio
async def test_get_content():
    async with aiohttp.ClientSession() as session:
        records = Context.get(
            queries=[ContentQuery(ark="bpt6k267221f", terms=["erratum"])],
            session=session,
        )
        list_records = [record async for record in records]
        context = list_records[0]
        assert context.ark == "bpt6k267221f"


@pytest.mark.asyncio
async def test_get_papers_wrapper():
    papers = await Papers.get(["cb32895690j"])
    paper = list(papers)[0]
    assert paper.code == "cb32895690j"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
