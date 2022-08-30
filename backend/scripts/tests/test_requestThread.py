from unittest import TestCase
from unittest.mock import patch, MagicMock
from requestThread import RequestThread
from scripts.requestTicket import RequestTicket


class TestRequestThread(TestCase):

    def test_init(self):
        testThread = RequestThread({}, '1')
        self.assertIsInstance(testThread, RequestThread)

    @patch('requestThread.RequestThread.moveRecordsToDB')
    @patch('requestThread.RequestThread.estimateIsUnderRecordLimit')
    @patch("requestThread.RequestThread.generateRequestTickets")
    @patch("requestThread.RequestTicket")
    def test_run(
            self,
            mock_ticket,
            mock_generate,
            mock_check_estimate,
            mock_move_records
    ):
        mock_ticket = MagicMock(
            run=MagicMock(return_value=MagicMock()),
            getEstimateNumberRecords=MagicMock(return_value=10)
        )
        mock_generate.return_value=[mock_ticket]
        testThread = RequestThread({'1': {}}, 'myrequestid')
        mock_check_estimate = MagicMock(return_value=True)

        testThread.run()

        mock_check_estimate.assert_called_with(10)
        mock_ticket.return_value.run.assert_called_once()
        mock_move_records.assert_called_once()

    def test_set_progress(self):
        testThread = RequestThread({})

        testThread.setTicketProgressStats('1', 10)

        self.assertEqual(testThread.ticketProgressStats['1'], 10)

    def test_get_progress(self):
        testThread = RequestThread({'1': {}})

        self.assertEqual(
            testThread.getProgressStats()['1'],
            {
                'progress': 0,
                'numResultsDiscovered': 0,
                'numResultsRetrieved': 0,
                'randomPaper': None,
                'estimateSecondsToCompletion': 0
            }
        )

    def test_set_num_discovered(self):
        testThread = RequestThread({})

        testThread.setNumDiscovered(10)

        self.assertEqual(testThread.numResultsDiscovered, 10)

    def test_get_num_discovered(self):
        testThread = RequestThread({})

        self.assertEqual(testThread.getNumDiscovered(), 0)

    def test_set_num_actually_retrieved(self):
        testThread = RequestThread({})

        testThread.setNumActuallyRetrieved(10)

        self.assertEqual(testThread.numResultsRetrieved, 10)

    def test_get_num_actually_retrieved(self):
        testThread = RequestThread({})

        self.assertEqual(testThread.getNumActuallyRetrieved(), 0)

    def test_move_records_to_db(self):
        testQuery = NgramQueryWithConcurrency('', [], '1234', MagicMock, MagicMock(cursor=MagicMock), MagicMock)
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
            TestNgramQueryWithConcurrency.cleanUpHoldingResults()
            dbConnection.close()

    @patch('scripts.ngramQueryWithConcurrency.Newspaper')
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
                    'd',
                    'id!'
                ]
            )
        except Exception as e:
            self.fail(e)
        finally:
            dbConnection.close()
            dbTester.deleteTestPapers()