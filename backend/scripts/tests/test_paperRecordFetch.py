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

    @staticmethod
    def deleteDummyPapersForTesting():
        tester = DBtester()
        tester.deleteAndReturnPaper('cb41459716t')
        tester.deleteAndReturnPaper('cb32690181n')
        tester.deleteAndReturnPaper('cb32751426x')
        tester.deleteAndReturnPaper('cb327808508')
        tester.deleteAndReturnPaper('cb32750493t')
        tester.deleteAndReturnPaper('cb32709443d')
        tester.deleteAndReturnPaper('cb327345882')
        tester.deleteAndReturnPaper('cb327514189')
        tester.deleteAndReturnPaper('cb32751344k')
        tester.deleteAndReturnPaper('cb32802219g')

    def test_fetch_record_data_for_codes(self):
        def boomerangBatchForTesting(batchItems):
            return [i for i in range(len(batchItems))]

        paperCodes20 = self.mockPaperCodes
        self.testInstance.fetchTheseMax20PaperRecords = MagicMock(
            side_effect=boomerangBatchForTesting
        )

        newspaper.test_fetch_record_data_for_codes(paperCodes20)

        self.assertEqual(
            len(newspaper.paperRecords),
            len(paperCodes20)
        )

        oneMissingPaper = Newspaper(MagicMock())
        oneMissingPaper.fetchTheseMax20PaperRecords = MagicMock(
            side_effect=boomerangBatchForTesting)
        oneMissingPaper.test_fetch_record_data_for_codes(["12345"])

        self.assertEqual(
            len(oneMissingPaper.paperRecords),
            1
        )

    @patch('scripts.newspaper.GallicaPaperRecordBatch')
    def test_fetch_max_20_paper_records(self, mock_paper_record_batch):
        mock_paper_record_batch.return_value = mock_paper_record_batch
        mock_paper_record_batch.getRecords = MagicMock(return_value=[])
        testCodes = self.mockPaperCodes

        records = self.testInstance.fetchTheseMax20PaperRecords(testCodes)

        self.assertEqual(len(records), 0)

    @patch('scripts.paperRecordFetch.PaperRecordFetch.fetchAllPapersFromGallica')
    def test_fetch_all_paper_records_on_gallica(self, mock_fetch):
        mock_fetch.return_value = '1'

        result = self.testInstance.fetchAllPaperRecordsOnGallica()

        self.assertEqual(
            result,
            '1'
        )

    def test_run_threaded_paper_fetch(self):
        pass

    def test_fetch_batch_papers_at_index(self):
        pass

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_get_num_papers_on_gallica(self, mock_get):
        with open(os.path.join(here, 'resources/dummyNewspaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        newspaper = Newspaper()
        numPapers = newspaper.getNumPapersOnGallica()
        self.assertEqual(numPapers, 18509)

