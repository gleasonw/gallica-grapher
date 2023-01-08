from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from gallicaGetter.gallicaWrapper import (
    VolumeOccurrenceWrapper,
    PeriodOccurrenceWrapper,
    IssuesWrapper,
    ContentWrapper,
    PapersWrapper,
    FullTextWrapper,
)


def connect(gallicaAPIselect, api=None, num_workers=15):
    api_wrappers = {
        "volume": VolumeOccurrenceWrapper,
        "period": PeriodOccurrenceWrapper,
        "issues": IssuesWrapper,
        "content": ContentWrapper,
        "papers": PapersWrapper,
        "text": FullTextWrapper,
    }
    select_api = gallicaAPIselect.lower()
    getter = api or ConcurrentFetch(numWorkers=num_workers)
    if select_api not in api_wrappers:
        raise ValueError(
            f'API "{select_api}" not supported. Options are {api_wrappers.keys()}'
        )
    return api_wrappers[select_api](api=getter)


if __name__ == "__main__":
    test = connect("sru")
    records = test.get(
        "brazza",
        startDate=1886,
        endDate=1890,
        startIndex=[0, 50, 214, 1008],
        grouping="index_selection",
    )
    print(records)
