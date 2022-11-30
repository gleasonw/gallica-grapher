from appsearch.search import AllSearch, GallicaGroupedSearch
from appsearch.search import build_searches_for_tickets
from appsearch.search import PyllicaSearch
from unittest import TestCase
from unittest.mock import MagicMock
from appsearch.search import get_num_periods_in_range_for_grouping


class Test(TestCase):
    def test_build(self):
        AllSearch.getAPIWrapper = MagicMock()
        PyllicaSearch.getAPIWrapper = MagicMock()
        GallicaGroupedSearch.getAPIWrapper = MagicMock()
        argBundles = {
            'all': {
                'grouping': 'all',
                'startDate': '1900',
                'endDate': '1901'
            },
            'year': {
                'grouping': 'year',
                'startDate': '1900',
                'endDate': '1901'
            },
            'month': {
                'grouping': 'month',
                'startDate': '1900',
                'endDate': '1901'
            },
            'yearWithCodes': {
                'grouping': 'year',
                'startDate': '1900',
                'endDate': '1901',
                'codes': ['A', 'B']
            },
            'monthWithCodes': {
                'grouping': 'month',
                'startDate': '1900',
                'endDate': '1901',
                'codes': ['A', 'B']
            }
        }
        searchObjs = build_searches_for_tickets(
            args_for_tickets=argBundles,
            stateHooks=MagicMock(),
            conn=MagicMock()
        )
        self.assertEqual(len(searchObjs), 5)
        self.assertIsInstance(searchObjs[0], AllSearch)
        self.assertIsInstance(searchObjs[1], PyllicaSearch)
        self.assertIsInstance(searchObjs[2], PyllicaSearch)
        self.assertIsInstance(searchObjs[3], GallicaGroupedSearch)
        self.assertIsInstance(searchObjs[4], GallicaGroupedSearch)

    def test_get_num_periods_in_range_for_grouping(self):
        self.assertEqual(
            get_num_periods_in_range_for_grouping(
                grouping='year',
                start='1900',
                end='1908'
            ),
            9
        )
        self.assertEqual(
            get_num_periods_in_range_for_grouping(
                grouping='month',
                start='1900',
                end='1908'
            ),
            108
        )


class TestSearch(TestCase):
    def setUp(self) -> None:
        initArgs = {
            'identifier': MagicMock(),
            'input_args': MagicMock(),
            'stateHooks': MagicMock(),
            'conn': MagicMock()
        }
        AllSearch.getAPIWrapper = MagicMock()
        self.searches = [
            AllSearch(**initArgs),
        ]

    # Liskov tests
    def test_responds_to_getNumRecordsToBeInserted(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'getNumRecordsToBeInserted'))

    def test_responds_to_getAPIWrapper(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'getAPIWrapper'))

    def test_responds_to_getDBinsert(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'getDBinsert'))

    # subclass responsibility tests
    def test_responds_to_post_init(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'post_init'))

    def test_responds_to_getLocalFetchArgs(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'getLocalFetchArgs'))


class TestAllSearch(TestCase):

    def setUp(self):
        AllSearch.getAPIWrapper = MagicMock()
        self.search = AllSearch(
            identifier=MagicMock(),
            input_args=MagicMock(),
            stateHooks=MagicMock(),
            conn=MagicMock()
        )

    def test_get_num_records_to_be_inserted(self):
        self.search.baseQueriesWithNumResults = [
            ('query1', 1),
            ('query2', 2),
        ]
        onNumRecordsFound = MagicMock()
        result = self.search.getNumRecordsToBeInserted(onNumRecordsFound)
        self.assertEqual(result, 3)
        onNumRecordsFound.assert_called_once_with(self.search, 3)

    def test_getLocalFetchArgs(self):
        self.search.baseQueriesWithNumResults = [
            ('query1', 1),
            ('query2', 2),
        ]
        result = self.search.getLocalFetchArgs()
        self.assertEqual(result['queriesWithCounts'], self.search.baseQueriesWithNumResults)
        self.assertTrue(result['generate'])
        self.assertIn('onUpdateProgress', result)


class TestPyllicaSearch(TestCase):

    def setUp(self):
        PyllicaSearch.getAPIWrapper = MagicMock()
        self.search = PyllicaSearch(
            identifier=MagicMock(),
            input_args=MagicMock(),
            stateHooks=MagicMock(),
            conn=MagicMock()
        )

    def test_getLocalFetchArgs(self):
        self.assertDictEqual(
            self.search.getLocalFetchArgs(),
            {
                'ticketID': self.search.identifier,
                'requestID': self.search.stateHooks.requestID,
            }
        )


class TestGallicaGroupedSearch(TestCase):

    def setUp(self):
        GallicaGroupedSearch.getAPIWrapper = MagicMock()
        self.search = GallicaGroupedSearch(
            identifier=MagicMock(),
            input_args=MagicMock(),
            stateHooks=MagicMock(),
            conn=MagicMock()
        )

    def test_get_num_records_to_be_inserted(self):
        self.search.args = {
            'grouping': 'year',
            'startDate': '1900',
            'endDate': '1901'
        }
        onRecordFound = MagicMock()
        result = self.search.getNumRecordsToBeInserted(onRecordFound)

        self.assertEqual(result, 2)
        onRecordFound.assert_called_once_with(self.search, 2)
