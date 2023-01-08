from unittest import TestCase
from unittest.mock import MagicMock
from gallicaGetter import connect
from gallicaGetter.gallicaWrapper import (
    VolumeOccurrenceWrapper,
    IssuesWrapper,
    ContentWrapper,
    PapersWrapper,
    FullTextWrapper,
    PeriodOccurrenceWrapper,
)


class TestGallicaWrapper(TestCase):
    def setUp(self) -> None:
        self.gallicaAPIs = [
            VolumeOccurrenceWrapper(api=MagicMock()),
            IssuesWrapper(api=MagicMock()),
            ContentWrapper(api=MagicMock()),
            PapersWrapper(api=MagicMock()),
        ]

    # Liskov tests
    def test_connect(self):
        self.assertIsInstance(connect("period"), PeriodOccurrenceWrapper)
        self.assertIsInstance(connect("volume"), VolumeOccurrenceWrapper)
        self.assertIsInstance(connect("issues"), IssuesWrapper)
        self.assertIsInstance(connect("content"), ContentWrapper)
        self.assertIsInstance(connect("papers"), PapersWrapper)
        self.assertIsInstance(connect("text"), FullTextWrapper)
        with self.assertRaises(ValueError):
            connect("not an api")


class TestVolumeOccurrenceWrapper(TestCase):
    def setUp(self) -> None:
        self.api = VolumeOccurrenceWrapper(api=MagicMock())

    def test_get(self):
        getter = VolumeOccurrenceWrapper(api=MagicMock())
        getter.api = MagicMock()
        getter.fetch_from_queries = MagicMock()

        self.assertIsInstance(getter.get(terms="a term"), list)


class TestPeriodOccurrenceWrapper(TestCase):
    def setUp(self) -> None:
        self.api = PeriodOccurrenceWrapper(api=MagicMock())

    def test_get(self):
        getter = PeriodOccurrenceWrapper(api=MagicMock())
        getter.api = MagicMock()
        getter.fetch_from_queries = MagicMock()

        self.assertIsInstance(getter.get(terms="a term"), list)


class TestIssuesWrapper(TestCase):
    def setUp(self) -> None:
        self.api = IssuesWrapper(api=MagicMock())

    def test_get(self):
        getter = IssuesWrapper(api=MagicMock())
        getter.queryBuilder = MagicMock()
        getter.fetch_from_queries = MagicMock()

        self.assertIsInstance(getter.get("a paper code"), list)


class TestContentWrapper(TestCase):
    def setUp(self) -> None:
        self.api = ContentWrapper(api=MagicMock())

    def test_get(self):
        getter = ContentWrapper(api=MagicMock())
        getter.queryBuilder = MagicMock()
        getter.fetch_from_queries = MagicMock()

        self.assertIsInstance(
            getter.get(ark="a periodical issue code", term="a term"), list
        )


class TestPapersWrapper(TestCase):
    def setUp(self) -> None:
        self.paperWrapper = PapersWrapper(api=MagicMock())

    def test_get(self):
        getter = PapersWrapper(api=MagicMock())
        getter.queryBuilder = MagicMock()
        getter.fetch_from_queries = MagicMock()
        getter.issues_wrapper = MagicMock()

        self.assertIsInstance(getter.get("a paper code"), list)


class TestFullTextWrapper(TestCase):
    def setUp(self) -> None:
        self.fullTextWrapper = FullTextWrapper(api=MagicMock())
        self.fullTextWrapper.fetch_from_queries = MagicMock()

    def test_get(self):
        records = self.fullTextWrapper.get("test")
        self.assertIsInstance(records, list)
