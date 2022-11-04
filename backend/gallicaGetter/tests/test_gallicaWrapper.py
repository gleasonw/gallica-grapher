from unittest import TestCase
from unittest.mock import MagicMock
from gallicaGetter import connect
from gallicaGetter.gallicaWrapper import SRUWrapper
from gallicaGetter.gallicaWrapper import IssuesWrapper
from gallicaGetter.gallicaWrapper import ContentWrapper
from gallicaGetter.gallicaWrapper import PapersWrapper
from gallicaGetter.parseRecord import ParseArkRecord
from gallicaGetter.parseRecord import ParsePaperRecords
from gallicaGetter.parseRecord import ParseContentRecord
from gallicaGetter.concurrentFetch import ConcurrentFetch
from gallicaGetter.queryBuilder import OccurrenceQueryBuilder
from gallicaGetter.queryBuilder import PaperQueryBuilder
from gallicaGetter.queryBuilder import ContentQueryFactory


class TestGallicaWrapper(TestCase):

    def setUp(self) -> None:
        self.gallicaAPIs = [
            SRUWrapper(),
            IssuesWrapper(),
            ContentWrapper(),
            PapersWrapper()
        ]

    #Liskov tests
    def test_responds_to_get(self):
        [self.assertTrue(hasattr(api, 'get')) for api in self.gallicaAPIs]

    #subclass responsibility tests
    def test_responds_to_preInit(self):
        [self.assertTrue(hasattr(api, 'preInit')) for api in self.gallicaAPIs]

    def test_responds_to_buildAPI(self):
        [self.assertTrue(hasattr(api, 'buildAPI')) for api in self.gallicaAPIs]

    def test_responds_to_buildQueryBuilder(self):
        [self.assertTrue(hasattr(api, 'buildQueryBuilder')) for api in self.gallicaAPIs]

    def test_responds_to_buildParser(self):
        [self.assertTrue(hasattr(api, 'buildParser')) for api in self.gallicaAPIs]

    def test_connect(self):
        self.assertIsInstance(connect('sru'), SRUWrapper)
        self.assertIsInstance(connect('issues'), IssuesWrapper)
        self.assertIsInstance(connect('content'), ContentWrapper)
        self.assertIsInstance(connect('papers'), PapersWrapper)
        with self.assertRaises(ValueError):
            connect('not an api')

#subclass state tests


class TestSRUWrapper(TestCase):

    def setUp(self) -> None:
        self.api = SRUWrapper()

    def test_buildAPI(self):
        self.assertIsInstance(self.api.buildAPI(10), ConcurrentFetch)

    def test_buildQueryBuilder(self):
        self.assertIsInstance(self.api.buildQueryBuilder(), OccurrenceQueryBuilder)

    def test_get(self):
        getter = SRUWrapper()
        getter.getFromQueries = MagicMock()

        self.assertIsInstance(
            getter.get(terms='a term'),
            list
        )


class TestIssuesWrapper(TestCase):

    def setUp(self) -> None:
        self.api = IssuesWrapper()

    def test_buildAPI(self):
        self.assertIsInstance(self.api.buildAPI(10), ConcurrentFetch)

    def test_buildQueryBuilder(self):
        self.assertIsInstance(self.api.buildQueryBuilder(), PaperQueryBuilder)

    def test_buildParser(self):
        self.assertIsInstance(self.api.buildParser(), ParseArkRecord)

    def test_get(self):
        getter = IssuesWrapper()
        getter.queryBuilder = MagicMock()
        getter.getFromQueries = MagicMock()

        self.assertIsInstance(
            getter.get('a paper code'),
            list
        )


class TestContentWrapper(TestCase):

        def setUp(self) -> None:
            self.api = ContentWrapper()

        def test_buildAPI(self):
            self.assertIsInstance(self.api.buildAPI(10), ConcurrentFetch)

        def test_buildQueryBuilder(self):
            self.assertIsInstance(self.api.buildQueryBuilder(), ContentQueryFactory)

        def test_buildParser(self):
            self.assertIsInstance(self.api.buildParser(), ParseContentRecord)

        def test_get(self):
            getter = ContentWrapper()
            getter.queryBuilder = MagicMock()
            getter.getFromQueries = MagicMock()

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

        def test_buildAPI(self):
            self.assertIsInstance(self.paperWrapper.buildAPI(10), ConcurrentFetch)

        def test_buildQueryBuilder(self):
            self.assertIsInstance(self.paperWrapper.buildQueryBuilder(), PaperQueryBuilder)

        def test_buildParser(self):
            self.assertIsInstance(self.paperWrapper.buildParser(), ParsePaperRecords)

        def test_get(self):
            #TODO: many dependencies.
            getter = PapersWrapper()
            getter.queryBuilder = MagicMock()
            getter.getFromQueries = MagicMock()
            getter.issuesWrapper = MagicMock()

            self.assertIsInstance(getter.get('a paper code'), list)