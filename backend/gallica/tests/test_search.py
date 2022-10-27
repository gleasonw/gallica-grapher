from search import Search
from search import build
from search import AllSearch
from search import GroupedSearch
from search import PaperSearch
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
        searchObjs = build(argBundles, stateHooks, wrapper=MagicMock())
        self.assertEqual(len(searchObjs), 3)
        self.assertIsInstance(searchObjs[0], AllSearch)
        self.assertIsInstance(searchObjs[1], GroupedSearch)
        self.assertIsInstance(searchObjs[2], GroupedSearch)


class TestSearch(TestCase):
    def setUp(self) -> None:
        initArgs = {
            'identifier': MagicMock(),
            'args': MagicMock(),
            'stateHooks': MagicMock(),
            'connectable': MagicMock()
        }
        self.searches = [
            AllSearch(**initArgs),
            GroupedSearch(**initArgs),
            PaperSearch(**initArgs)
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
            args=MagicMock(),
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
        self.assertDictEqual(
            self.search.getLocalFetchArgs(),
            {
                'queriesWithCounts' : self.search.baseQueriesWithNumResults,
                'generate': True
            }
        )


class TestGroupedSearch(TestCase):

    def setUp(self) -> None:
        initArgs = {
            'identifier': MagicMock(),
            'args': MagicMock(),
            'stateHooks': MagicMock(),
            'connectable': MagicMock()
        }
        self.yearSearch = GroupedSearch(
            **{
                **initArgs,
                'args': {
                    'grouping': 'year',
                    'startDate': '1900',
                    'endDate': '1901'
                }
            }
        )
        self.monthSearch = GroupedSearch(
            **{
                **initArgs,
                'args': {
                    'grouping': 'month',
                    'startDate': '1900',
                    'endDate': '1901'
                }
            }
        )

    def test_get_num_records_to_be_inserted_when_month_grouped(self):
        onNumRecordsFound = MagicMock()
        self.assertEqual(
            self.monthSearch.getNumRecordsToBeInserted(onNumRecordsFound),
            24
        )
        onNumRecordsFound.assert_called_once_with(self.monthSearch, 24)

    def test_get_num_records_to_be_inserted_when_year_grouped(self):
        onNumRecordsFound = MagicMock()
        self.assertEqual(
            self.yearSearch.getNumRecordsToBeInserted(onNumRecordsFound),
            2
        )
        onNumRecordsFound.assert_called_once_with(self.yearSearch, 2)

    def test_more_date_intervals_than_record_batches_when_many_results(self):
        self.monthSearch.api.getNumResultsForArgs = MagicMock(return_value=[(None, 10000)])
        self.assertFalse(self.monthSearch.moreDateIntervalsThanRecordBatches())

    def test_more_date_intervals_than_record_batches_when_few_results(self):
        self.monthSearch.api.getNumResultsForArgs = MagicMock(return_value=[(None, 1)])
        self.assertTrue(self.monthSearch.moreDateIntervalsThanRecordBatches())




