from gallicaGetter.gallicaWrapper import (
    VolumeOccurrenceWrapper,
    PeriodOccurrenceWrapper,
    IssuesWrapper,
    ContentWrapper,
    PapersWrapper,
    FullTextWrapper
)


def connect(gallicaAPIselect, **kwargs):
    api_wrappers = {
        'volume': VolumeOccurrenceWrapper,
        'period_count': PeriodOccurrenceWrapper,
        'issues': IssuesWrapper,
        'content': ContentWrapper,
        'papers': PapersWrapper,
        'text': FullTextWrapper
    }
    api = gallicaAPIselect.lower()
    if api not in api_wrappers:
        raise ValueError(f'API "{api}" not supported. Options are {api_wrappers.keys()}')
    return api_wrappers[api](**kwargs)


if __name__ == '__main__':
    test = connect('sru')
    records = test.get(
        'brazza',
        startDate=1886,
        endDate=1890,
        startIndex=[0, 50, 214, 1008],
        grouping='index_selection'
    )
    print(records)
