from gallicaGetter.gallicaWrapper import SRUWrapper
from gallicaGetter.gallicaWrapper import IssuesWrapper
from gallicaGetter.gallicaWrapper import ContentWrapper
from gallicaGetter.gallicaWrapper import PapersWrapper
from gallicaGetter.gallicaWrapper import FullTextWrapper


def connect(gallicaAPIselect, **kwargs):
    apiWrappers = {
        'sru': SRUWrapper,
        'issues': IssuesWrapper,
        'content': ContentWrapper,
        'papers': PapersWrapper,
        'text': FullTextWrapper
    }
    api = gallicaAPIselect.lower()
    if api not in apiWrappers:
        raise ValueError(f'API "{api}" not supported. Options are {apiWrappers.keys()}')
    return apiWrappers[api](**kwargs)


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
