from scripts.recordsToDBTransaction import RecordsToDBTransaction
from unittest import TestCase
from unittest.mock import patch, MagicMock
from utils.psqlconn import PSQLconn
from DBtester import DBtester


class TestRecordsToDBTransaction(TestCase):

    def setUp(self):
        self.testTransaction = RecordsToDBTransaction(
            'testrequest',
            MagicMock()
        )

    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.insertPapers')
    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.insertNgramOccurrenceRecords')
    def test_insert(self, mock_insert_ngram, mock_insert_papers):

        self.testTransaction.insert('papers', 'records')
        mock_insert_papers.assert_called_once_with('records')

        self.testTransaction.insert('results', 'ngramrecords')
        mock_insert_ngram.assert_called_once_with('ngramrecords')

        with self.assertRaises(ValueError):
            self.testTransaction.insert('badtable', 'badrecords')

    @patch('scripts.recordsToDBTransaction.io')
    def test_insert_papers(self, mock_io):
        self.testTransaction.conn.copy_from = MagicMock()
        mock_io.StringIO.return_value = MagicMock()

        self.testTransaction.insertPapers(MagicMock())

        self.testTransaction.conn.copy_from.assert_called_once()

    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.addMissingPapers')
    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.moveRecordsToFinalTable')
    @patch('scripts.recordsToDBTransaction.io')
    def test_insert_ngram_occurrence_records(self, mock_io, mock_move, mock_add):
        self.testTransaction.conn.copy_from = MagicMock()
        mock_io.StringIO.return_value = MagicMock()

        self.testTransaction.insertNgramOccurrenceRecords(MagicMock())

        self.testTransaction.conn.copy_from.assert_called_once()
        mock_add.assert_called_once()
        mock_move.assert_called_once()

    @patch('scripts.recordsToDBTransaction.PaperRecordFetch')
    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.getMissingPapers')
    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.insert')
    def test_add_missing_papers(self, mock_insert, mock_get, mock_fetch):
        mock_get.return_value = ['testpaperid']
        mock_fetch.test_fetch_record_data_for_codes.return_value = 'testrecords'
        mock_fetch.return_value = mock_fetch

        self.testTransaction.addMissingPapers()

        mock_fetch.assert_called_once()
        mock_insert.assert_called_once_with('papers', 'testrecords')

    def test_get_missing_papers(self):
        self.testTransaction.conn.cursor.return_value.__enter__.return_value.execute = MagicMock()

        self.testTransaction.getMissingPapers()

        self.testTransaction.conn.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            """
                WITH papersInResults AS 
                    (SELECT DISTINCT paperid 
                    FROM holdingResults 
                    WHERE requestid = %s)
                SELECT paperid FROM papersInResults
                WHERE paperid NOT IN 
                    (SELECT code FROM papers);
                """,
            ('testrequest',)
        )

    def test_move_records_to_final_table(self):
        self.testTransaction.conn.cursor.return_value.__enter__.return_value.execute = MagicMock()

        self.testTransaction.moveRecordsToFinalTable()

        self.testTransaction.conn.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            """
                WITH resultsForRequest AS (
                    DELETE FROM holdingresults
                    WHERE requestid = %s
                    RETURNING identifier, year, month, day, searchterm, paperid, ticketid, requestid
                )
                INSERT INTO results (identifier, year, month, day, searchterm, paperid, ticketid, requestid)
                    (SELECT identifier, year, month, day , searchterm, paperid, ticketid, requestid 
                    FROM resultsForRequest);
                """,
            ('testrequest',)
        )

    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.addMissingPapers')
    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.moveRecordsToFinalTable')
    def test_move_mock_records_to_holding(self, mock_move, mock_add):
        self.testTransaction.conn = PSQLconn().getConn()
        records = self.get5MockKeywordRecords()

        self.testTransaction.insert('results', records)

        testRecords = DBtester().deleteAndReturnTestResultsInHolding()

        self.assertEqual(len(testRecords), 5)

    def test_move_mock_papers_to_papers(self):
        self.testTransaction.conn = PSQLconn().getConn()
        records = self.get5MockPaperRecords()

        self.testTransaction.insert('papers', records)

        testRecords = DBtester().deleteAndReturnTestPapers()

        self.assertEqual(len(testRecords), 5)

    @staticmethod
    def get5MockKeywordRecords():
        payload = []
        ngrams = ['t', 'te', 'ter', 'term', 'term!']
        codes = ['a', 'b', 'c', 'd', 'e']
        ticketIDs = ['1', '2', '3', '4', '5']
        for i in range(5):
            mockRecord = MagicMock()
            mockRecord.getDate = MagicMock(return_value=[1920, 10, 1])
            mockRecord.getUrl = MagicMock(return_value='1234.com')
            mockRecord.getKeyword = MagicMock(return_value=ngrams[i])
            mockRecord.getPaperCode = MagicMock(return_value=codes[i])
            mockRecord.getTicketID = MagicMock(return_value=ticketIDs[i])
            payload.append(mockRecord)

        return payload

    @staticmethod
    def get5MockPaperRecords():
        payload = []
        codes = ['a', 'b', 'c', 'd', 'e']
        for i in range(5):
            mockRecord = MagicMock()
            mockRecord.getPaperCode = MagicMock(return_value=codes[i])
            mockRecord.getPaperTitle = MagicMock(return_value='test title')
            mockRecord.isContinuous = MagicMock(return_value=True)
            mockRecord.getDate = MagicMock(return_value=[1920, 1930])
            payload.append(mockRecord)

        return payload