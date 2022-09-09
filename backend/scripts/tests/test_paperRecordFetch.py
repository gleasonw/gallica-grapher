import unittest
from unittest.mock import MagicMock, patch
import os
from DBtester import DBtester
from scripts.paperRecordFetch import PaperRecordFetch

here = os.path.dirname(__file__)


class TestPaperRecordFetch(unittest.TestCase):

    def setUp(self):
        self.testDB = DBtester()
        self.testInstance = PaperRecordFetch()
        with open(os.path.join(here, "resources/newspaper_codes")) as f:
            self.mockPaperCodes = f.read().splitlines()
        with open(os.path.join(here, 'resources/20PaperRecords.xml'), "rb") as f:
            self.mockedPaperFetch = MagicMock(content=f.read())

    @patch('scripts.paperRecordFetch.PaperRecordFetch.fetchTheseMax20PaperRecords')
    def test_fetch_record_data_for_codes(self, mock_batch_20_fetch):
        mock_batch_20_fetch.side_effect = lambda x: x

        records = self.testInstance.fetchPaperRecordsForCodes(self.mockPaperCodes)

        self.assertEqual(
            len(records),
            len(self.mockPaperCodes)
        )

    @patch('scripts.paperRecordFetch.GallicaPaperRecordBatch')
    def test_fetch_max_20_paper_records(self, mock_paper_record_batch):
        mock_paper_record_batch.return_value = mock_paper_record_batch
        mock_paper_record_batch.getRecords = MagicMock(return_value=[])
        testCodes = self.mockPaperCodes

        records = self.testInstance.fetchTheseMax20PaperRecords(testCodes)

        self.assertEqual(len(records), 0)

    @patch('scripts.paperRecordFetch.PaperRecordFetch.fetchAllPaperRecordsOnGallica')
    def test_fetch_all_paper_records_on_gallica(self, mock_fetch):
        mock_fetch.return_value = '1'

        result = self.testInstance.fetchAllPaperRecords()

        self.assertEqual(
            result,
            '1'
        )

    @patch('scripts.paperRecordFetch.PaperRecordFetch.getNumPapersOnGallica')
    @patch('scripts.paperRecordFetch.PaperRecordFetch.fetchBatchPapersAtIndex')
    def test_run_threaded_paper_fetch(self, mock_fetch, mock_get):
        mock_get.return_value = 100
        mock_fetch.side_effect = lambda x: [x]

        result = self.testInstance.fetchPapersConcurrently()

        self.assertListEqual(
            result,
            [1, 51]
        )

    @patch('scripts.paperRecordFetch.GallicaPaperRecordBatch')
    def test_fetch_batch_papers_at_index(self, mock_batch):
        mock_batch.getRecords = MagicMock(return_value='itworks?')
        mock_batch.return_value = mock_batch

        result = self.testInstance.fetchBatchPapersAtIndex(1)

        self.assertEqual(
            result,
            'itworks?'
        )

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_get_num_papers_on_gallica(self, mock_get):
        with open(os.path.join(here, 'resources/dummyNewspaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        numPapers = self.testInstance.getNumPapersOnGallica()
        self.assertEqual(numPapers, 18509)

