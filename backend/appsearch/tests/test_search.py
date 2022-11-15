from appsearch.search import AllSearch
from appsearch.search import buildSearch
from appsearch.search import GroupedSearch
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
            }
        }
        stateHooks = MagicMock()
        searchObjs = buildSearch(argBundles, stateHooks, wrapper=MagicMock())
        self.assertEqual(len(searchObjs), 3)
        self.assertIsInstance(searchObjs[0], AllSearch)
        self.assertIsInstance(searchObjs[1], GroupedSearch)
        self.assertIsInstance(searchObjs[2], GroupedSearch)


class TestSearch(TestCase):
    def setUp(self) -> None:
        initArgs = {
            'identifier': MagicMock(),
            'input_args': MagicMock(),
            'stateHooks': MagicMock(),
            'connectable': MagicMock()
        }
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
        self.search = AllSearch(
            identifier=MagicMock(),
            input_args=MagicMock(),
            stateHooks=MagicMock(),
            connectable=MagicMock()
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