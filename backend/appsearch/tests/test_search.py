from appsearch.search import AllSearch, GallicaGroupedSearch
from appsearch.search import build_searches_for_tickets
from appsearch.search import PyllicaSearch
from unittest import TestCase
from unittest.mock import MagicMock


class Test(TestCase):
    def test_build(self):
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
        stateHooks = MagicMock()
        searchObjs = build_searches_for_tickets(argBundles, stateHooks)
        self.assertEqual(len(searchObjs), 5)
        self.assertIsInstance(searchObjs[0], AllSearch)
        self.assertIsInstance(searchObjs[1], PyllicaSearch)
        self.assertIsInstance(searchObjs[2], PyllicaSearch)
        self.assertIsInstance(searchObjs[3], GallicaGroupedSearch)
        self.assertIsInstance(searchObjs[4], GallicaGroupedSearch)


class TestSearch(TestCase):
    def setUp(self) -> None:
        initArgs = {
            'identifier': MagicMock(),
            'input_args': MagicMock(),
            'stateHooks': MagicMock(),
        }
        AllSearch.getAPIWrapper = MagicMock()
        self.searches = [
            AllSearch(**initArgs),
        ]

    #Liskov tests
    def test_responds_to_getNumRecordsToBeInserted(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'getNumRecordsToBeInserted'))

    def test_responds_to_getAPIWrapper(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'getAPIWrapper'))

    def test_responds_to_getDBinsert(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'getDBinsert'))

    #subclass responsibility tests
    def test_responds_to_post_init(self):
        for search in self.searches:
            self.assertTrue(hasattr(search, 'postInit'))

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
        local_args = self.search.getLocalFetchArgs()
        self.assertEqual(local_args['generate'], True)
        self.assertEqual(local_args['queriesWithCounts'], self.search.baseQueriesWithNumResults)
        self.assertIn('onUpdateProgress', local_args)