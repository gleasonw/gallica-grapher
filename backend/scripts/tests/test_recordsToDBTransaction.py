from scripts.recordsToDBTransaction import RecordsToDBTransaction
from unittest import TestCase
from unittest.mock import patch, MagicMock
from psqlconn import PSQLconn


class TestRecordsToDBTransaction(TestCase):

    def setUp(self):
        testConn = PSQLconn().getConn()
        self.testTransaction = RecordsToDBTransaction(
            'testrequestid',
            testConn
        )

    def tearDown(self):
        self.testTransaction.conn.close()

    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.insertPapers')
    @patch('scripts.recordsToDBTransaction.RecordsToDBTransaction.insertNgramOccurrenceRecords')
    def test_insert(self, mock_insert_ngram, mock_insert_papers):

        self.testTransaction.insert('papers', 'records')
        mock_insert_papers.assert_called_once_with('records')

        self.testTransaction.insert('results', 'ngramrecords')
        mock_insert_ngram.assert_called_once_with('ngramrecords')

        with self.assertRaises(ValueError):
            self.testTransaction.insert('badtable', 'badrecords')

    @patch('scripts.recordsToDBTransaction.generateRecordCSVStream')
    def test_insert_papers(self):
        self.fail()

    def test_insert_ngram_occurrence_records(self):
        self.fail()

    def test_add_missing_papers(self):
        self.fail()

    def test_get_missing_papers(self):
        self.fail()

    def test_move_records_to_final_table(self):
        self.fail()

    def test_generate_result_csv_stream(self):
        self.fail()

    def test_get_paper_record_row_iterable(self):
        self.fail()

    def test_get_keyword_record_row_iterable(self):
        self.fail()