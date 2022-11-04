from .gallicaWrapper import SRUWrapper
from .gallicaWrapper import IssuesWrapper
from .gallicaWrapper import ContentWrapper
from .gallicaWrapper import PapersWrapper


def connect(gallicaAPIselect, **kwargs):
    apiWrappers = {
        'sru': SRUWrapper,
        'issues': IssuesWrapper,
        'content': ContentWrapper,
        'papers': PapersWrapper,
    }
    api = gallicaAPIselect.lower()
    if api not in apiWrappers:
        raise ValueError(f'API "{api}" not supported. Options are {apiWrappers.keys()}')
    return apiWrappers[api](**kwargs)
