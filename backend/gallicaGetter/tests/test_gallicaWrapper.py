import pytest
from gallicaGetter.contentWrapper import ContextWrapper
from gallicaGetter.issuesWrapper import IssuesWrapper
from gallicaGetter.papersWrapper import PapersWrapper

from gallicaGetter.volumeOccurrenceWrapper import VolumeOccurrenceWrapper
from gallicaGetter.periodOccurrenceWrapper import PeriodOccurrenceWrapper


# could speed up by running the fetches in parallel. But hey, sometimes it's good to relax
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
    ],
)
async def test_get_volume_occurrences(input, expected_length):
    getter = VolumeOccurrenceWrapper()
    records = await getter.get(**input, get_all_results=True)
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
    getter = PeriodOccurrenceWrapper()
    records = await getter.get(**input)
    list_records = list(records)
    assert len(list_records) == expected_length


@pytest.mark.asyncio
async def test_get_issues():
    getter = IssuesWrapper()
    records = await getter.get("cb344484501")
    list_records = list(records)
    assert len(list_records) == 1
    issue = list_records[0]
    assert issue.code == "cb344484501"


@pytest.mark.asyncio
async def test_get_content():
    getter = ContextWrapper()
    records = await getter.get([("bpt6k267221f", ["erratum"])])
    list_records = list(records)
    context = list_records[0]
    assert context.ark == "bpt6k267221f"


@pytest.mark.asyncio
async def test_get_papers_wrapper():
    getter = PapersWrapper()
    papers = await getter.get(["cb32895690j"])
    paper = papers[0]
    assert paper.code == "cb32895690j"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
