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
    def connect_content(self, api: Optional[Gettable] = None):
        return ContentWrapper(api=api or ConcurrentFetch(numWorkers=20))

    def connect_volume(self, api: Optional[Gettable] = None):
        return VolumeOccurrenceWrapper(api=api or ConcurrentFetch(numWorkers=20))

    def connect_period(self, api: Optional[Gettable] = None):
        return PeriodOccurrenceWrapper(api=api or ConcurrentFetch(numWorkers=20))

    def connect_issues(self, api: Optional[Gettable] = None):
        return IssuesWrapper(api=api or ConcurrentFetch(numWorkers=20))

    def connect_papers(self, api: Optional[Gettable] = None):
        return PapersWrapper(api=api or ConcurrentFetch(numWorkers=20))

    def connect_full_text(self, api: Optional[Gettable] = None):
        return FullTextWrapper(api=api or ConcurrentFetch(numWorkers=20))
