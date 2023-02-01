from typing import Optional
from gallicaGetter.fetch.concurrentFetch import ConcurrentFetch
from gallicaGetter.gallicaWrapper import (
    VolumeOccurrenceWrapper,
    PeriodOccurrenceWrapper,
    IssuesWrapper,
    ContentWrapper,
    PapersWrapper,
    FullTextWrapper,
)


class Gettable:
    def get(self):
        return


class WrapperFactory:
    @staticmethod
    def connect_context(api: Optional[Gettable] = None):
        return ContentWrapper(api=api or ConcurrentFetch(numWorkers=20))

    @staticmethod
    def connect_volume(api: Optional[Gettable] = None):
        return VolumeOccurrenceWrapper(api=api or ConcurrentFetch(numWorkers=20))

    @staticmethod
    def connect_period(api: Optional[Gettable] = None):
        return PeriodOccurrenceWrapper(api=api or ConcurrentFetch(numWorkers=20))

    @staticmethod
    def connect_issues(api: Optional[Gettable] = None):
        return IssuesWrapper(api=api or ConcurrentFetch(numWorkers=20))

    @staticmethod
    def connect_papers(api: Optional[Gettable] = None):
        return PapersWrapper(api=api or ConcurrentFetch(numWorkers=20))

    @staticmethod
    def connect_full_text(api: Optional[Gettable] = None):
        return FullTextWrapper(api=api or ConcurrentFetch(numWorkers=20))
