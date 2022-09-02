from unittest import TestCase
from unittest.mock import MagicMock, patch
from psqlconn import PSQLconn
from scripts.ngramQueryWithConcurrency import NgramQueryWithConcurrency
from scripts.ngramQueryWithConcurrency import NgramQueryWithConcurrencyAllPapers
from scripts.ngramQueryWithConcurrency import NgramQueryWithConcurrencySelectPapers
from utils.gallicaSession import GallicaSession
from DBtester import DBtester
import os

here = os.path.dirname(__file__)


class TestNgramQueryWithConcurrency(TestCase):

    def test_establish_year_range(self):
        noRangeQuery = NgramQueryWithConcurrency(
            '',
            [],
            '1234',
            MagicMock,
            MagicMock,
            MagicMock
        )
        rangeQuery = NgramQueryWithConcurrency(
            '',
            [1, 1],
            '1234',
            MagicMock,
            MagicMock,
            MagicMock
        )
        self.assertFalse(noRangeQuery.isYearRange)
        self.assertTrue(rangeQuery.isYearRange)

    def test_build_no_year_range_query(self):
        noRangeQuery = NgramQueryWithConcurrency(
            '',
            [],
            '1234',
            MagicMock,
            MagicMock,
            MagicMock
        )
        noRangeQuery.buildDatelessQuery = MagicMock()

        noRangeQuery.buildQuery()

        self.assertTrue(noRangeQuery.buildDatelessQuery.called)

    def test_build_year_range_query(self):
        rangeQuery = NgramQueryWithConcurrency(
            '',
            [1, 1],
            '1234',
            MagicMock,
            MagicMock,
            MagicMock
        )
        rangeQuery.buildYearRangeQuery = MagicMock()

        rangeQuery.buildQuery()

        self.assertTrue(rangeQuery.buildYearRangeQuery.called)

    def test_run_search(self):
        testQuery = NgramQueryWithConcurrency(
            '',
            [],
            '1234',
            MagicMock,
            MagicMock,
            GallicaSession().getSession())
        testQuery.generateWorkChunks = MagicMock()
        testQuery.doThreadedSearch = MagicMock()
        testQuery.moveRecordsToDB = MagicMock()

        testQuery.runSearch()

        self.assertTrue(testQuery.generateWorkChunks.called)
        self.assertTrue(testQuery.doThreadedSearch.called)
        self.assertFalse(testQuery.moveRecordsToDB.called)

    def test_do_threaded_search(self):
        testQuery = NgramQueryWithConcurrency(
            '',
            [],
            '1234',
            MagicMock,
            MagicMock,
            GallicaSession().getSession())
        testQuery.workChunks = [1, 2, 3, 4]
        testQuery.progressTracker = MagicMock()
        testQuery.doSearchChunk = MagicMock(
            side_effect=lambda x: MagicMock(
                getRecords=MagicMock(return_value=[x])))

        testQuery.doThreadedSearch()

        self.assertTrue(testQuery.doSearchChunk.called)
        self.assertEqual(testQuery.doSearchChunk.call_count, 4)
        self.assertTrue(testQuery.progressTracker.called)
        self.assertListEqual(
            testQuery.keywordRecords,
            [1, 2, 3, 4]
        )

    # TODO: test cases insufficient... check null case


class TestNgramQueryWithConcurrencyAllPapers(TestCase):

    def test_build_year_range_query(self):
        NgramQueryWithConcurrencyAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = NgramQueryWithConcurrencyAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQuery,
            'dc.date >= "1850" and dc.date <= "1900" '
            'and (gallica adj "brazza") '
            'and (dc.type adj "fascicule") '
            'sortby dc.date/sort.ascending')

    def test_build_dateless_query(self):
        NgramQueryWithConcurrencyAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = NgramQueryWithConcurrencyAllPapers(
            'brazza',
            [],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQuery,
            '(gallica adj "brazza") '
            'and (dc.type adj "fascicule") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.ngramQueryWithConcurrency.GallicaRecordBatch')
    def test_fetch_num_total_results(self, mock_batch):
        mock_batch = mock_batch.return_value
        mock_batch.getNumResults = MagicMock(return_value=3)
        query = NgramQueryWithConcurrencyAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
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
        query = NgramQueryWithConcurrencyAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(query.doSearchChunk(1), mock_keyword_batch)

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencyAllPapers.fetchNumTotalResults')
    def test_generate_work_chunks(self, mock_total_results):
        query = NgramQueryWithConcurrencyAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )
        query.estimateNumResults = 123

        query.generateWorkChunks()

        self.assertListEqual(
            query.workChunks,
            [1, 51, 101]
        )


class TestNgramQueryWithConcurrencySelectPapers(TestCase):

    def buildDummyDict(self):
        with open(os.path.join(here, "resources/dummy_newspaper_choice_dicts")) as f:
            dummyNewspaperChoices = f.read().splitlines()
            choiceDict = []
            for nameCode in dummyNewspaperChoices:
                nameCode = nameCode.split(',')
                choiceDict.append(
                    {'name': nameCode[0].strip(),
                     'code': nameCode[1].strip()})
            return choiceDict

    def test_build_year_range_query(self):
        NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults = MagicMock(return_value=3)

        choiceDict = self.buildDummyDict()
        query = NgramQueryWithConcurrencySelectPapers(
            'brazza',
            choiceDict,
            [1850, 1900],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertEqual(
            query.baseQuery,
            'arkPress adj "{newsKey}_date" '
            'and dc.date >= "1850" '
            'and dc.date <= "1900" '
            'and (gallica adj "brazza") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumberResultsInPaper')
    def test_build_dateless_query(self, mock_fetch):
        mock_fetch.return_value = ['a', 1]
        choiceDict = self.buildDummyDict()

        query = NgramQueryWithConcurrencySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertEqual(
            query.baseQuery,
            'arkPress adj "{newsKey}_date" '
            'and (gallica adj "brazza") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumberResultsInPaper')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    def test_set_num_results_for_each_paper(self, mock_fetch, mock_fetch_paper):
        mock_fetch_paper.return_value = ['b', 1]

        query = NgramQueryWithConcurrencySelectPapers(
            'brazza',
            [{'name': 'a', 'code': 'b'}],
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        query.sumResultsForEachPaperQuery()

        self.assertDictEqual(query.paperCodeWithNumResults, {'b': 1})

    @patch('scripts.ngramQueryWithConcurrency.GallicaRecordBatch.fetchXML')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    @patch('scripts.ngramQueryWithConcurrency.GallicaRecordBatch.getNumResults', return_value=3)
    def test_fetch_number_results_in_paper(self, mock_getNumResults, mock_fetch, mock_fetch_xml):
        choiceDict = self.buildDummyDict()
        query = NgramQueryWithConcurrencySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        resultTest = query.fetchNumResultsForQuery({'code': 'a'})

        self.assertEqual(
            resultTest,
            ('a', 3))

    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    def test_sum_up_paper_results_for_total_estimate(self, mock_fetch):
        choiceDict = self.buildDummyDict()
        query = NgramQueryWithConcurrencySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())
        query.paperCodeWithNumResults = {'a': 1, 'b': 2}
        query.sumUpQueryResultsForTotalEstimate()

        self.assertEqual(
            query.estimateNumResults,
            3)

    def test_generate_work_chunks(self):
        choiceDict = self.buildDummyDict()
        NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults = MagicMock()
        query = NgramQueryWithConcurrencySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())
        query.paperCodeWithNumResults = {'a': 125, 'b': 256}

        query.generateWorkChunks()

        self.assertListEqual(
            query.workChunks,
            [
                [1, 'a'], [51, 'a'], [101, 'a'],
                [1, 'b'], [51, 'b'], [101, 'b'], [151, 'b'], [201, 'b'], [251, 'b']
            ]
        )

    @patch('scripts.ngramQueryWithConcurrency.GallicaKeywordRecordBatch')
    @patch('scripts.ngramQueryWithConcurrency.NgramQueryWithConcurrencySelectPapers.fetchNumTotalResults')
    def test_do_search_chunk(self, mock_total_results, mock_record_batch):
        choiceDict = self.buildDummyDict()
        mockedSession = MagicMock()
        query = NgramQueryWithConcurrencySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            mockedSession)

        testBatch = query.doSearchChunk([1, 'a'])

        mock_record_batch.assert_called_with(
            'arkPress adj "a_date" '
            'and (gallica adj "brazza") '
            'sortby dc.date/sort.ascending',
            mockedSession,
            startRecord=1
        )
