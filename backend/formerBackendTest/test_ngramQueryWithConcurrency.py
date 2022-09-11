from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from cqlforticket import CQLforTicket
from cqlforticket import QueriesAllPapers
from cqlforticket import QueriesSelectPapers
from utils.gallicaSession import GallicaSession
import os

here = os.path.dirname(__file__)


class TestNgramQueryWithConcurrency(TestCase):

    def setUp(self) -> None:
        self.testQuery = CQLforTicket(
            '',
            [],
            '1234',
            'myrequest',
            MagicMock,
            MagicMock,
            MagicMock)

    def test_establish_year_range(self):
        noRangeQuery = CQLforTicket(
            '',
            [],
            '1234',
            'myrequest',
            MagicMock,
            MagicMock,
            MagicMock
        )
        rangeQuery = CQLforTicket(
            '',
            [1, 1],
            '1234',
            'myrequest',
            MagicMock,
            MagicMock,
            MagicMock
        )
        self.assertFalse(noRangeQuery.isYearRange)
        self.assertTrue(rangeQuery.isYearRange)

    def test_build_no_year_range_query(self):
        noRangeQuery = CQLforTicket(
            '',
            [],
            '1234',
            'myrequest',
            MagicMock,
            MagicMock,
            MagicMock
        )
        noRangeQuery.buildDatelessQuery = MagicMock()

        noRangeQuery.attachCQL()

        self.assertTrue(noRangeQuery.buildDatelessQuery.called)

    def test_build_year_range_query(self):
        rangeQuery = CQLforTicket(
            '',
            [1, 1],
            '1234',
            'myrequest',
            MagicMock,
            MagicMock,
            MagicMock
        )
        rangeQuery.buildYearRangeQuery = MagicMock()

        rangeQuery.attachCQL()

        self.assertTrue(rangeQuery.buildYearRangeQuery.called)

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrency.doThreadedSearch')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrency.generateWorkChunks')
    @patch('scripts.ngramQueryWithConcurrency.RecordsToDBTransaction')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrency.splitIntoCHUNK_SIZEchunks')
    def test_run_search(self, mock_split, mock_transact, mock_chunk, mock_search):
        mock_transact.insert = MagicMock()
        mock_transact.return_value = mock_transact
        mock_split.return_value = [1, 2]

        self.testQuery.runSearch()

        self.assertTrue(mock_chunk.called)
        mock_search.assert_has_calls([
            call(1),
            call(2)
        ])
        mock_transact.insert.assert_has_calls([
            call('results', mock_search.return_value),
            call('results', mock_search.return_value)
        ])

    def test_do_threaded_search(self):
        testQuery = CQLforTicket(
            '',
            [],
            '1234',
            'myrequest',
            MagicMock,
            MagicMock,
            GallicaSession().getSession())
        workChunks = [1, 2, 3, 4]
        testQuery.progressTracker = MagicMock()
        testQuery.doSearchChunk = MagicMock(
            side_effect=lambda x: MagicMock(
                getRecords=MagicMock(return_value=[x])))

        results = testQuery.doThreadedSearch(workChunks)

        self.assertTrue(testQuery.doSearchChunk.called)
        self.assertEqual(testQuery.doSearchChunk.call_count, 4)
        self.assertTrue(testQuery.progressTracker.called)
        self.assertListEqual(
            results,
            [1, 2, 3, 4]
        )

    # TODO: test cases insufficient... check null case


class TestNgramQueryWithConcurrencyAllPapers(TestCase):

    def test_build_year_range_query(self):
        QueriesAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = QueriesAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            'myrequest',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQueryComponents,
            'dc.date >= "1850" and dc.date <= "1900" '
            'and (gallica adj "brazza") '
            'and (dc.type adj "fascicule") '
            'sortby dc.date/sort.ascending')

    def test_build_dateless_query(self):
        QueriesAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = QueriesAllPapers(
            'brazza',
            [],
            '1234',
            'myrequest',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQueryComponents,
            '(gallica adj "brazza") '
            'and (dc.type adj "fascicule") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.ngramQueryWithConcurrency.GallicaRecordBatch')
    def test_fetch_num_total_results(self, mock_batch):
        mock_batch = mock_batch.return_value
        mock_batch.getNumResults = MagicMock(return_value=3)
        query = QueriesAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            'myrequest',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(query.fetchNumTotalResults(), 3)

    @patch('scripts.ngramQueryWithConcurrency.GallicaRecordBatch')
    @patch('scripts.ngramQueryWithConcurrency.GallicaKeywordRecordBatch')
    def test_do_search_chunk(self, mock_keyword_batch, mock_record_batch):
        mock_keyword_batch = mock_keyword_batch.return_value
        mock_record_batch = mock_record_batch.return_value
        mock_record_batch.getNumResults = MagicMock(return_value=3)
        mock_keyword_batch.getRecords = MagicMock(return_value='batch!')
        query = QueriesAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            'myrequest',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(query.doSearchChunk(1), mock_keyword_batch)

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencyAllPapers.fetchNumTotalResults')
    def test_generate_work_chunks(self, mock_total_results):
        query = QueriesAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            'myrequest',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )
        query.estimateNumResults = 123

        chunks = query.generateWorkChunks()

        self.assertListEqual(
            chunks,
            [1, 51, 101]
        )


class TestNgramQueryWithConcurrencySelectPapers(TestCase):

    @patch('scripts.ngramQueryWithConcurrency.CQLSelectStringForPapers')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    def setUp(self, mock_fetch, mock_cql) -> None:
        self.query = QueriesSelectPapers(
            'brazza',
            ['a'],
            [1850, 1900],
            '1234',
            'myrequest',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

    def getMockCodes(self):
        with open(os.path.join(here, "backend/formerBackendTest/resources/newspaper_codes")) as f:
            dummyNewspaperChoices = f.read().splitlines()
            return dummyNewspaperChoices

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.buildQueriesForPaperCodes')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    def test_build_year_range_query(self, mock_fetch, mock_build):
        mock_fetch.return_value = 3

        choiceDict = self.getMockCodes()
        query = QueriesSelectPapers(
            'brazza',
            choiceDict,
            [1850, 1900],
            '1234',
            'myrequest',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertEqual(
            query.baseQueryComponents,
            '({formattedCodeString}) '
            'and dc.date >= "1850" '
            'and dc.date <= "1900" '
            'and (gallica adj "brazza") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.buildQueriesForPaperCodes')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    def test_build_dateless_query(self, mock_fetch, mock_build):
        mock_fetch.return_value = ['a', 1]
        choiceDict = self.getMockCodes()

        query = QueriesSelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            'myrequest',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertEqual(
            query.baseQueryComponents,
            '({formattedCodeString}) '
            'and (gallica adj "brazza") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    @patch('scripts.ngramQueryWithConcurrency.CQLSelectStringForPapers')
    def test_build_queries_for_paper_codes(self, mock_cql, mock_fetch):
        choiceDict = self.getMockCodes()
        mock_cql.return_value=MagicMock(
            cqlSelectStrings=[1, 2])

        query = QueriesSelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            'myrequest',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertListEqual(
            query.queries,
            ['(1) '
            f'and (gallica adj "brazza") '
            'sortby dc.date/sort.ascending',
             '(2) '
             f'and (gallica adj "brazza") '
             'sortby dc.date/sort.ascending'
             ]
        )

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumResultsForQuery')
    def test_set_num_results_for_queries(self, mock_fetch_query):
        mock_fetch_query.return_value = [1, 'arkPress all "cb41459716t_date"']
        self.query.queries = ['test']
        self.query.numResultsInQueries = {}

        self.query.setNumResultsForQueries()

        self.assertDictEqual(self.query.numResultsInQueries, {'cb41459716t': 1})

    @patch('scripts.ngramQueryWithConcurrency.GallicaRecordBatch.fetchXML')
    @patch('scripts.ngramQueryWithConcurrency.GallicaRecordBatch.getNumResults', return_value=3)
    def test_fetch_num_results_for_query(self, mock_getNumResults, mock_fetch_xml):
        resultTest = self.query.fetchNumResultsForQuery('arkpressyadayada')

        self.assertEqual(
            resultTest,
            (3, 'arkpressyadayada'))

    def test_sum_up_query_results_for_total_estimate(self):
        self.query.numResultsInQueries = {'a': 1, 'b': 2}
        self.query.sumUpQueryResultsForTotalEstimate()

        self.assertEqual(
            self.query.estimateNumResults,
            3)

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.generateIndicesForCQLQueries')
    def test_generate_work_chunks(self, mock_generate):
        mock_generate.return_value = ['neat']

        test = self.query.generateWorkChunks()

        self.assertListEqual(
            test,
            ['n','e','a','t']
        )

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.getIndicesForCQLQuery')
    def test_generate_indices_for_cql_queries(self, mock_gen):
        self.query.queries = ['a', 'b', 'c']

        test = self.query.generateIndicesForCQLQueries()
        for neat in test:
            print(neat)

        self.assertEqual(mock_gen.call_count, 3)

    def test_get_indices_for_cql_query(self):
        self.query.numResultsInQueries['cb32895690j'] = 289
        query = 'arkPress all "cb32895690j_date"'

        test = self.query.getIndicesForCQLQuery(query)

        self.assertListEqual(
            test,
            [
                [1, query],
                [51, query],
                [101, query],
                [151, query],
                [201, query],
                [251, query]]
        )

    @patch('scripts.ngramQueryWithConcurrency.GallicaKeywordRecordBatch')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    def test_do_search_chunk(self, mock_total_results, mock_record_batch):
        mockedSession = MagicMock()
        self.query.gallicaHttpSession = mockedSession

        self.query.doSearchChunk([1, 'a'])

        mock_record_batch.assert_called_with(
            '(a) '
            f'and dc.date >= "1850" '
            f'and dc.date <= "1900" '
            f'and (gallica adj "brazza") '
            'sortby dc.date/sort.ascending',
            '1234',
            'brazza',
            mockedSession,
            startRecord=1
        )
