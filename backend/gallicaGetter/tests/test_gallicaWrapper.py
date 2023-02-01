import pytest

from backend.contextPair import ContextPair
from ..wrapperFactory import WrapperFactory

# could speed up by running the fetches in parallel. But hey, sometimes it's good to relax
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
def test_get_volume_occurrences(input, expected_length):
    getter = WrapperFactory.connect_volume()
    records = getter.get(**input)
    list_records = list(records)
    assert len(list_records) == expected_length


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
def test_get_period_occurrences(input, expected_length):
    getter = WrapperFactory.connect_period()
    records = getter.get(**input)
    list_records = list(records)
    assert len(list_records) == expected_length


def test_get_issues():
    getter = WrapperFactory.connect_issues()
    records = getter.get("cb344484501")
    list_records = list(records)
    assert len(list_records) == 1
    issue = list_records[0]
    assert issue.code == "cb344484501"


def test_get_content():
    getter = WrapperFactory.connect_context()()
    records = getter.get([ContextPair(ark_code="bpt6k267221f", term="erratum")])
    list_records = list(records)
    context = list_records[0]
    assert context.ark == "bpt6k267221f"


def test_get_papers_wrapper():
    getter = WrapperFactory.connect_papers()
    papers = getter.get("cb32895690j")
    paper = papers[0]
    assert paper.code == "cb32895690j"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
