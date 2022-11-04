from unittest import TestCase
from gallicaGetter.recordGetter import RecordGetter
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

    #superclass responsibility tests
    def test_buildRecordGetter(self):
        self.assertIsInstance(self.gallicaAPIs[0].buildRecordGetter(), RecordGetter)

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


class TestIssuesWrapper(TestCase):

    def setUp(self) -> None:
        self.api = IssuesWrapper()

    def test_buildAPI(self):
        self.assertIsInstance(self.api.buildAPI(10), ConcurrentFetch)

    def test_buildQueryBuilder(self):
        self.assertIsInstance(self.api.buildQueryBuilder(), PaperQueryBuilder)

    def test_buildParser(self):
        self.assertIsInstance(self.api.buildParser(), ParseArkRecord)


class TestContentWrapper(TestCase):

        def setUp(self) -> None:
            self.api = ContentWrapper()

        def test_buildAPI(self):
            self.assertIsInstance(self.api.buildAPI(10), ConcurrentFetch)

        def test_buildQueryBuilder(self):
            self.assertIsInstance(self.api.buildQueryBuilder(), ContentQueryFactory)

        def test_buildParser(self):
            self.assertIsInstance(self.api.buildParser(), ParseContentRecord)


class TestPapersWrapper(TestCase):

        def setUp(self) -> None:
            self.api = PapersWrapper()

        def test_buildAPI(self):
            self.assertIsInstance(self.api.buildAPI(10), ConcurrentFetch)

        def test_buildQueryBuilder(self):
            self.assertIsInstance(self.api.buildQueryBuilder(), PaperQueryBuilder)

        def test_buildParser(self):
            self.assertIsInstance(self.api.buildParser(), ParsePaperRecords)
