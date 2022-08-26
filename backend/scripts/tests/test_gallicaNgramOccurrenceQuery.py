from unittest import TestCase
from unittest.mock import MagicMock, patch
from scripts.psqlconn import PSQLconn
from scripts.gallicaNgramOccurrenceQuery import GallicaNgramOccurrenceQuery
from scripts.gallicaNgramOccurrenceQuery import GallicaNgramOccurrenceQueryAllPapers
from scripts.gallicaNgramOccurrenceQuery import GallicaNgramOccurrenceQuerySelectPapers
from scripts.gallicaSession import GallicaSession
from DBtester import DBtester
import os

here = os.path.dirname(__file__)


class TestGallicaNgramOccurrenceQuery(TestCase):

    @staticmethod
    def cleanUpHoldingResults():
        dbConnection = PSQLconn().getConn()
        with dbConnection.cursor() as curs:
            curs.execute(
                """
                DELETE FROM holdingresults WHERE requestid = 'id!';
                """)
        dbConnection.close()

    @patch('gallicaRecord.GallicaRecord')
    def getMockBatchOf5KeywordRecords(self, mock_record):
        mock_record.return_value = mock_record
        mock_record.parsePaperCodeFromXML = MagicMock(return_value="123")
        mock_record.parseURLFromXML = MagicMock(return_value="http://example.com")

        payload = GallicaNgramOccurrenceQuery(
            'term!',
            [],
            'id!',
            MagicMock,
            MagicMock,
            MagicMock
        )
        codes = ['a', 'b', 'c', 'd', 'e']
        for i in range(5):
            mockRecord = MagicMock()
            mockRecord.getDate = MagicMock(return_value=[1920, 10, 1])
            mockRecord.getUrl = MagicMock(return_value='1234.com')
            mockRecord.getPaperCode = MagicMock(return_value=codes[i])
            mockRecord.parseDateFromXML = MagicMock()
            mockRecord.checkIfValid = MagicMock()
            payload.keywordRecords.append(mockRecord)

        return payload

    def test_establish_year_range(self):
        noRangeQuery = GallicaNgramOccurrenceQuery(
            '',
            [],
            '1234',
            MagicMock,
            MagicMock,
            MagicMock
        )
        rangeQuery = GallicaNgramOccurrenceQuery(
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
        noRangeQuery = GallicaNgramOccurrenceQuery(
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
        rangeQuery = GallicaNgramOccurrenceQuery(
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
        testQuery = GallicaNgramOccurrenceQuery(
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
        testQuery = GallicaNgramOccurrenceQuery(
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

    def test_move_records_to_db(self):
        testQuery = GallicaNgramOccurrenceQuery('', [], '1234', MagicMock, MagicMock(cursor=MagicMock), MagicMock)
        testQuery.moveRecordsToHoldingResultsDB = MagicMock()
        testQuery.moveRecordsToFinalTable = MagicMock()
        testQuery.addMissingPapers = MagicMock()

        testQuery.moveRecordsToDB()

        self.assertTrue(testQuery.moveRecordsToHoldingResultsDB.called)
        self.assertTrue(testQuery.moveRecordsToFinalTable.called)
        self.assertTrue(testQuery.addMissingPapers.called)

    def test_move_records_to_holding_db(self):
        dbConnection = PSQLconn().getConn()
        payload = self.getMockBatchOf5KeywordRecords()
        payload.dbConnection = dbConnection
        payload.addMissingPapers = MagicMock
        payload.moveRecordsToFinalTable = MagicMock
        dbTester = DBtester()

        payload.moveRecordsToHoldingResultsDB(dbConnection.cursor())

        postedResults = dbTester.deleteAndReturnTestResultsInHolding()
        firstRow = list(postedResults[0])
        self.assertEqual(len(postedResults), 5)
        self.assertListEqual(
            firstRow,
            [
                '1234.com',
                1920,
                10,
                1,
                'term!',
                'a',
                'id!'
            ]
        )

    def test_generate_result_CSV_stream(self):
        payload = self.getMockBatchOf5KeywordRecords()
        testStream = payload.generateResultCSVstream()
        streamRows = testStream.getvalue().split("\n")
        firstStreamRow = streamRows[0].split("|")

        self.assertEqual(len(streamRows), 6)
        self.assertEqual(firstStreamRow[0], "1234.com")
        self.assertEqual(firstStreamRow[1], '1920')
        self.assertEqual(firstStreamRow[2], '10')
        self.assertEqual(firstStreamRow[3], '1')
        self.assertEqual(firstStreamRow[4], "term!")
        self.assertEqual(firstStreamRow[5], "a")
        self.assertEqual(firstStreamRow[6], "id!")

    # TODO: test cases insufficient... check null case
    def test_get_missing_papers(self):
        dbConnection = PSQLconn().getConn()
        payload = self.getMockBatchOf5KeywordRecords()
        payload.dbConnection = dbConnection
        payload.moveRecordsToFinalTable = MagicMock
        payload.addMissingPapers = MagicMock
        try:

            payload.moveRecordsToHoldingResultsDB(dbConnection.cursor())
            missing = payload.getMissingPapers(dbConnection.cursor())

            self.assertEqual(len(missing), 5)
            self.assertListEqual(
                sorted(missing),
                [('a',), ('b',), ('c',), ('d',), ('e',)])

        except Exception as e:
            self.fail(e)
        finally:
            TestGallicaNgramOccurrenceQuery.cleanUpHoldingResults()
            dbConnection.close()

    @patch('scripts.gallicaNgramOccurrenceQuery.Newspaper')
    def test_add_missing_papers(self, mock_paper):
        mock_paper = mock_paper.return_value
        mock_paper.sendTheseGallicaPapersToDB = MagicMock()
        payload = self.getMockBatchOf5KeywordRecords()
        payload.getMissingPapers = MagicMock()

        payload.addMissingPapers(MagicMock)

        self.assertTrue(payload.getMissingPapers.called)
        self.assertTrue(mock_paper.sendTheseGallicaPapersToDB.called)

    @patch('scripts.gallicaNgramOccurrenceQuery.Newspaper')
    def test_add_missing_papers_when_no_missing_papers(self, mock_paper):
        mock_paper = mock_paper.return_value
        mock_paper.sendTheseGallicaPapersToDB = MagicMock()
        payload = self.getMockBatchOf5KeywordRecords()
        payload.getMissingPapers = MagicMock(return_value=[])

        payload.addMissingPapers(MagicMock)

        self.assertTrue(payload.getMissingPapers.called)
        self.assertFalse(mock_paper.sendTheseGallicaPapersToDB.called)

    def test_move_records_to_final_table(self):
        dbConnection = PSQLconn().getConn()
        payload = self.getMockBatchOf5KeywordRecords()
        payload.dbConnection = dbConnection
        dbTester = DBtester()
        dbTester.insertTestPapers()
        try:
            payload.moveRecordsToHoldingResultsDB(dbConnection.cursor())
            payload.moveRecordsToFinalTable(dbConnection.cursor())

            postedResults = dbTester.deleteAndReturnTestResultsInFinal()
            firstRow = list(postedResults[0])
            self.assertEqual(len(postedResults), 5)
            self.assertListEqual(
                firstRow,
                [
                    '1234.com',
                    1920,
                    10,
                    1,
                    'term!',
                    'a',
                    'id!'
                ]
            )
        except Exception as e:
            self.fail(e)
        finally:
            dbConnection.close()
            dbTester.deleteTestPapers()


class TestGallicaNgramOccurrenceQueryAllPapers(TestCase):

    def test_build_year_range_query(self):
        GallicaNgramOccurrenceQueryAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = GallicaNgramOccurrenceQueryAllPapers(
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
            'and (scripts all "brazza") '
            'and (dc.type adj "fascicule") '
            'sortby dc.date/sort.ascending')

    def test_build_dateless_query(self):
        GallicaNgramOccurrenceQueryAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = GallicaNgramOccurrenceQueryAllPapers(
            'brazza',
            [],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQuery,
            '(scripts all "brazza") '
            'and (dc.type adj "fascicule") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaRecordBatch')
    def test_fetch_num_total_results(self, mock_batch):
        mock_batch = mock_batch.return_value
        mock_batch.getNumResults = MagicMock(return_value=3)
        query = GallicaNgramOccurrenceQueryAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(query.fetchNumTotalResults(), 3)

    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaRecordBatch')
    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaKeywordRecordBatch')
    def test_do_search_chunk(self, mock_keyword_batch, mock_record_batch):
        mock_keyword_batch = mock_keyword_batch.return_value
        mock_record_batch = mock_record_batch.return_value
        mock_record_batch.getNumResults = MagicMock(return_value=3)
        mock_keyword_batch.getRecords = MagicMock(return_value='batch!')
        query = GallicaNgramOccurrenceQueryAllPapers(
            'brazza',
            [1850, 1900],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(query.doSearchChunk(1), mock_keyword_batch)

    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQueryAllPapers.fetchNumTotalResults')
    def test_generate_work_chunks(self, mock_total_results):
        query = GallicaNgramOccurrenceQueryAllPapers(
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


class TestGallicaNgramOccurrenceQuerySelectPapers(TestCase):

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
        GallicaNgramOccurrenceQuerySelectPapers.fetchNumTotalResults = MagicMock(return_value=3)

        choiceDict = self.buildDummyDict()
        query = GallicaNgramOccurrenceQuerySelectPapers(
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
            'and (scripts all "brazza") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.fetchNumberResultsInPaper')
    def test_build_dateless_query(self, mock_fetch):
        mock_fetch.return_value = ['a', 1]
        choiceDict = self.buildDummyDict()

        query = GallicaNgramOccurrenceQuerySelectPapers(
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
            'and (scripts all "brazza") '
            'sortby dc.date/sort.ascending')

    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.fetchNumberResultsInPaper')
    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.fetchNumTotalResults')
    def test_set_num_results_for_each_paper(self, mock_fetch, mock_fetch_paper):
        mock_fetch_paper.return_value = ['b', 1]

        query = GallicaNgramOccurrenceQuerySelectPapers(
            'brazza',
            [{'name': 'a', 'code': 'b'}],
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        query.setNumResultsForEachPaper()

        self.assertDictEqual(query.paperCodeWithNumResults, {'b': 1})

    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaRecordBatch.fetchXML')
    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.fetchNumTotalResults')
    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaRecordBatch.getNumResults', return_value=3)
    def test_fetch_number_results_in_paper(self, mock_getNumResults, mock_fetch, mock_fetch_xml):
        choiceDict = self.buildDummyDict()
        query = GallicaNgramOccurrenceQuerySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        resultTest = query.fetchNumberResultsInPaper({'code': 'a'})

        self.assertEqual(
            resultTest,
            ('a', 3))

    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.fetchNumTotalResults')
    def test_sum_up_paper_results_for_total_estimate(self, mock_fetch):
        choiceDict = self.buildDummyDict()
        query = GallicaNgramOccurrenceQuerySelectPapers(
            'brazza',
            choiceDict,
            [],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())
        query.paperCodeWithNumResults = {'a': 1, 'b': 2}
        query.sumUpPaperResultsForTotalEstimate()

        self.assertEqual(
            query.estimateNumResults,
            3)

    def test_generate_work_chunks(self):
        choiceDict = self.buildDummyDict()
        GallicaNgramOccurrenceQuerySelectPapers.fetchNumTotalResults = MagicMock()
        query = GallicaNgramOccurrenceQuerySelectPapers(
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

    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaKeywordRecordBatch')
    @patch('scripts.gallicaNgramOccurrenceQuery.GallicaNgramOccurrenceQuerySelectPapers.fetchNumTotalResults')
    def test_do_search_chunk(self, mock_total_results, mock_record_batch):
        choiceDict = self.buildDummyDict()
        mockedSession = MagicMock()
        query = GallicaNgramOccurrenceQuerySelectPapers(
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
            'and (scripts all "brazza") '
            'sortby dc.date/sort.ascending',
            mockedSession,
            startRecord=1
        )
