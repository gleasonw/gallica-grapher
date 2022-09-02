from unittest import TestCase
from unittest.mock import patch, MagicMock
from request import Request
from scripts.ticket import Ticket
from scripts.ngramQueryWithConcurrency import NgramQueryWithConcurrency
from psqlconn import PSQLconn
from DBtester import DBtester


class TestRequest(TestCase):

    def test_init(self):
        testThread = Request({}, '1')
        self.assertIsInstance(testThread, Request)

    @patch('request.Request.moveRecordsToDB')
    @patch('request.Request.estimateIsUnderRecordLimit')
    @patch("request.Request.generateRequestTickets")
    @patch("request.Ticket")
    def test_run(
            self,
            mock_ticket,
            mock_generate,
            mock_check_estimate,
            mock_move_records
    ):
        mock_ticket.run = MagicMock()
        mock_ticket.getEstimateNumberRecords = MagicMock(return_value=10)
        mock_generate.return_value = [mock_ticket]
        testThread = Request({'1': {}}, 'myrequestid')

        testThread.run()

        mock_check_estimate.assert_called_with(10)
        mock_ticket.run.assert_called_once()
        mock_move_records.assert_called_once()

    @patch('request.Ticket')
    def test_generate_request_tickets(self, mock_ticket):
        mock_ticket.return_value = mock_ticket
        testRequest = Request({}, '1')
        testRequest.ticketDicts = {
            '1': {},
            '2': {}
        }

        generatedTickets = testRequest.generateRequestTickets()

        self.assertEqual(len(generatedTickets), 2)
        self.assertEqual(generatedTickets[0], mock_ticket)

    @patch('request.Request.getNumberRowsInAllTables')
    def test_estimate_is_under_record_limit(self, mock_get):
        testThread = Request({}, '1')
        mock_get.return_value = 1000000

        self.assertTrue(testThread.estimateIsUnderRecordLimit(100))
        self.assertFalse(testThread.estimateIsUnderRecordLimit(100000000))

    def test_set_progress(self):
        testThread = Request({}, '1')

        testThread.setTicketProgressStats('1', 10)

        self.assertEqual(testThread.ticketProgressStats['1'], 10)

    def test_get_progress(self):
        testThread = Request({'1': {}}, '1')

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
        testThread = Request({}, '1')

        testThread.setNumDiscovered(10)

        self.assertEqual(testThread.numResultsDiscovered, 10)

    def test_get_num_discovered(self):
        testThread = Request({}, '1')

        self.assertEqual(testThread.getNumDiscovered(), 0)

    def test_set_num_actually_retrieved(self):
        testThread = Request({}, '1')

        testThread.setNumActuallyRetrieved(10)

        self.assertEqual(testThread.numResultsRetrieved, 10)

    def test_get_num_actually_retrieved(self):
        testThread = Request({}, '1')

        self.assertEqual(testThread.getNumActuallyRetrieved(), 0)

    def test_move_records_to_db(self):
        testThread = Request({}, '1')
        testThread.moveRecordsToHoldingResultsDB = MagicMock()
        testThread.moveRecordsToFinalTable = MagicMock()
        testThread.addMissingPapers = MagicMock()

        testThread.moveRecordsToDB()

        self.assertTrue(testThread.moveRecordsToHoldingResultsDB.called)
        self.assertTrue(testThread.moveRecordsToFinalTable.called)
        self.assertTrue(testThread.addMissingPapers.called)

    def test_move_records_to_holding_db(self):
        payload = self.getRequestWith5MockRecords()
        dbTester = DBtester()
        testCursor = dbTester.conn.cursor()

        payload.moveRecordsToHoldingResultsDB(testCursor)

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
                't',
                'a',
                '1',
                'testrequest'
            ]
        )

    def test_generate_result_CSV_stream(self):
        payload = self.getRequestWith5MockRecords()
        testStream = payload.generateResultCSVstream()
        streamRows = testStream.getvalue().split("\n")
        firstStreamRow = streamRows[0].split("|")
        secondStreamRow = streamRows[1].split("|")

        self.assertEqual(len(streamRows), 6)
        self.assertEqual(streamRows[5], '')
        self.assertListEqual(
            firstStreamRow,
            ['1234.com', '1920', '10', '1', 't', 'a', '1', 'testrequest']
        )
        self.assertListEqual(
            secondStreamRow,
            ['1234.com', '1920', '10', '1', 'te', 'b', '2', 'testrequest']
        )

    def test_get_missing_papers(self):
        payload = self.getRequestWith5MockRecords()
        testCursor = self.dbTester.conn.cursor()
        try:

            payload.moveRecordsToHoldingResultsDB(testCursor)
            missing = payload.getMissingPapers(testCursor)

            self.assertEqual(len(missing), 5)
            self.assertListEqual(
                sorted(missing),
                [('a',), ('b',), ('c',), ('d',), ('e',)])

        except Exception as e:
            self.fail(e)
        finally:
            self.dbTester.deleteTestResultsFromHolding()

    @patch('request.Newspaper')
    def test_add_missing_papers(self, mock_paper):
        mock_paper = mock_paper.return_value
        mock_paper.sendTheseGallicaPapersToDB = MagicMock()
        payload = self.getRequestWith5MockRecords()
        payload.getMissingPapers = MagicMock()

        payload.addMissingPapers(MagicMock)

        self.assertTrue(payload.getMissingPapers.called)
        self.assertTrue(mock_paper.sendTheseGallicaPapersToDB.called)

    @patch('request.Newspaper')
    def test_add_missing_papers_when_no_missing_papers(self, mock_paper):
        mock_paper = mock_paper.return_value
        mock_paper.sendTheseGallicaPapersToDB = MagicMock()
        payload = self.getRequestWith5MockRecords()
        payload.getMissingPapers = MagicMock(return_value=[])

        payload.addMissingPapers(MagicMock)

        self.assertTrue(payload.getMissingPapers.called)
        self.assertFalse(mock_paper.sendTheseGallicaPapersToDB.called)

    def test_move_records_to_final_table(self):
        payload = self.getRequestWith5MockRecords()
        self.dbTester.insertTestPapers()
        testCursor = self.dbTester.conn.cursor()
        try:
            payload.moveRecordsToHoldingResultsDB(testCursor)
            payload.moveRecordsToFinalTable(testCursor)

            postedResults = self.dbTester.deleteAndReturnTestResultsInFinal()
            firstRow = list(postedResults[0])
            self.assertEqual(len(postedResults), 5)
            self.assertListEqual(
                firstRow,
                [
                    '1234.com',
                    1920,
                    10,
                    1,
                    't',
                    'a',
                    '1',
                    'testrequest'
                ]
            )
        except Exception as e:
            self.fail(e)
        finally:
            self.dbTester.deleteTestPapers()
