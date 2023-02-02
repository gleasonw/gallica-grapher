from typing import Optional
from gallicaGetter.concurrentFetch import ConcurrentFetch
from gallicaGetter.contentWrapper import ContextWrapper
from gallicaGetter.volumeOccurrenceWrapper import VolumeOccurrenceWrapper
from gallicaGetter.periodOccurrenceWrapper import PeriodOccurrenceWrapper
from gallicaGetter.issuesWrapper import IssuesWrapper
from gallicaGetter.papersWrapper import PapersWrapper
from gallicaGetter.fullTextWrapper import FullTextWrapper


class Gettable:
    def get(self):
        return


NUM_WORKERS = 30


class WrapperFactory:
    @staticmethod
    def context(api: Optional[Gettable] = None):
        return ContextWrapper(api=api or ConcurrentFetch(numWorkers=NUM_WORKERS))

    @staticmethod
    def volume(api: Optional[Gettable] = None):
        return VolumeOccurrenceWrapper(
            api=api or ConcurrentFetch(numWorkers=NUM_WORKERS)
        )

    @staticmethod
    def period(api: Optional[Gettable] = None):
        return PeriodOccurrenceWrapper(
            api=api or ConcurrentFetch(numWorkers=NUM_WORKERS)
        )

    @staticmethod
    def issues(api: Optional[Gettable] = None):
        return IssuesWrapper(api=api or ConcurrentFetch(numWorkers=NUM_WORKERS))

    @staticmethod
    def papers(api: Optional[Gettable] = None):
        return PapersWrapper(api=api or ConcurrentFetch(numWorkers=NUM_WORKERS))

    @staticmethod
    def full_text(api: Optional[Gettable] = None):
        return FullTextWrapper(api=api or ConcurrentFetch(numWorkers=NUM_WORKERS))
