from unittest import TestCase
from fetch.concurrentfetch import ConcurrentFetch
from fetch.concurrentfetch import NUM_WORKERS
from unittest.mock import patch, MagicMock, call

from fetch.fetch import get


class TestFetch(TestCase):

    def setUp(self) -> None:
        self.numWorkers = NUM_WORKERS
        self.fetch = ConcurrentFetch(None)

    @patch('fetch.Fetch.get')
    def test_fetch_all_given_queries_exist(self, mock_get):
        queries = ['test1', 'test2']
        test = self.fetch.fetchAll(queries)
        self.assertIsInstance(test, list)
        for result in test:
            self.assertEqual(result, mock_get.return_value)

    @patch('fetch.Fetch.get')
    def test_fetch_all_given_queries_empty(self, mock_get):
        queries = []

        test = self.fetch.fetchAll(queries)

        self.assertIsInstance(test, list)

    @patch('fetch.Fetch.get')
    def test_fetch_all_and_track_progress_given_queries_exist(self, mock_get):
        queries = ['test1', 'test2']
        tracker = MagicMock()

        test = self.fetch.fetchAllAndTrackProgress(queries, tracker)

        self.assertIsInstance(test, list)
        for result in test:
            self.assertEqual(result, mock_get.return_value)
        tracker.assert_has_calls(
            [
                call(mock_get.return_value, self.numWorkers),
                call(mock_get.return_value, self.numWorkers)
            ]
        )

    @patch('fetch.Fetch.getParamsFor')
    def test_get(self, mock_params):
        mock_params.return_value = 'testParams'
        self.fetch.http = MagicMock()
        self.fetch.http.request.return_value = MagicMock()
        self.fetch.http.request.return_value.data = 'testData'
        self.fetch.http.request.return_value.elapsed.total_seconds.return_value = 1.0
        query = MagicMock()

        test = get(self.fetch.http, self.fetch.baseUrl, query)

        self.fetch.http.request.assert_has_calls(
            [call('GET', None, fields='testParams')
             ])
        self.assertEqual(test, query)
        self.assertEqual(query.responseXML, 'testData')
        self.assertEqual(query.elapsedTime, 1.0)

    def test_get_params_for(self):
        query = MagicMock()
        query.cql = 'testUrl'
        query.startIndex = 1
        query.numRecords = 2
        query.collapsing = 'testCollapsing'

        test = self.fetch.getParamsFor(query)

        self.assertEqual(test, {
            'operation': 'searchRetrieve',
            'exactSearch': 'True',
            'version': 1.2,
            'startRecord': 1,
            'maximumRecords': 2,
            'collapsing': 'testCollapsing',
            'query': 'testUrl'
        })
