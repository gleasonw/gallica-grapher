from unittest import TestCase
from unittest.mock import MagicMock
from gallicaGetter import connect
from gallicaGetter.gallicaWrapper import (
    SRUWrapper,
    IssuesWrapper,
    ContentWrapper,
    PapersWrapper,
    FullTextWrapper,
)
from gallicaGetter.parse.parseRecord import (
    ParseArkRecord,
    ParseContentRecord
)
from gallicaGetter.build.queryBuilder import (
    OccurrenceQueryBuilder,
    PaperQueryBuilder,
    ContentQueryBuilder
)


class TestGallicaWrapper(TestCase):

    def setUp(self) -> None:
        self.gallicaAPIs = [
            SRUWrapper(),
            IssuesWrapper(),
            ContentWrapper(),
            PapersWrapper()
        ]

    #Liskov tests
    def test_connect(self):
        self.assertIsInstance(connect('sru'), SRUWrapper)
        self.assertIsInstance(connect('issues'), IssuesWrapper)
        self.assertIsInstance(connect('content'), ContentWrapper)
        self.assertIsInstance(connect('papers'), PapersWrapper)
        self.assertIsInstance(connect('text'), FullTextWrapper)
        with self.assertRaises(ValueError):
            connect('not an api')


class TestSRUWrapper(TestCase):

    def setUp(self) -> None:
        self.api = SRUWrapper()

    def test_getQueryBuilder(self):
        self.assertIsInstance(self.api.getQueryBuilder(), OccurrenceQueryBuilder)

    def test_get(self):
        getter = SRUWrapper()
        getter.fetchFromQueries = MagicMock()

        self.assertIsInstance(
            getter.get(terms='a term'),
            list
        )


class TestIssuesWrapper(TestCase):

    def setUp(self) -> None:
        self.api = IssuesWrapper()

    def test_getQueryBuilder(self):
        self.assertIsInstance(self.api.getQueryBuilder(), PaperQueryBuilder)

    def test_buildParser(self):
        self.assertIsInstance(self.api.parser, ParseArkRecord)

    def test_get(self):
        getter = IssuesWrapper()
        getter.queryBuilder = MagicMock()
        getter.fetchFromQueries = MagicMock()

        self.assertIsInstance(
            getter.get('a paper code'),
            list
        )


class TestContentWrapper(TestCase):

        def setUp(self) -> None:
            self.api = ContentWrapper()

        def test_getQueryBuilder(self):
            self.assertIsInstance(self.api.getQueryBuilder(), ContentQueryBuilder)

        def test_buildParser(self):
            self.assertIsInstance(self.api.parser, ParseContentRecord)

        def test_get(self):
            getter = ContentWrapper()
            getter.queryBuilder = MagicMock()
            getter.fetchFromQueries = MagicMock()

            self.assertIsInstance(
                getter.get(
                    ark='a periodical issue code',
                    term='a term'
                ),
                list
            )


class TestPapersWrapper(TestCase):

        def setUp(self) -> None:
            self.paperWrapper = PapersWrapper()

        def test_getQueryBuilder(self):
            self.assertIsInstance(self.paperWrapper.getQueryBuilder(), PaperQueryBuilder)

        def test_get(self):
            getter = PapersWrapper()
            getter.queryBuilder = MagicMock()
            getter.fetchFromQueries = MagicMock()
            getter.issuesWrapper = MagicMock()

            self.assertIsInstance(getter.get('a paper code'), list)


class TestFullTextWrapper(TestCase):

    def setUp(self) -> None:
        self.fullTextWrapper = FullTextWrapper()

    def test_getQueryBuilder(self):
        self.fail()

    def test_get(self):
        self.fail()