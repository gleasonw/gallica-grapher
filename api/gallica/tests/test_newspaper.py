from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.newspaper import Newspaper
import os

here = os.path.dirname(__file__)


class TestNewspaper(TestCase):

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_fetch_record_data_from_code_strings(self, mock_get):
        with open(os.path.join(here, 'data/20PaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        newspaper = Newspaper()
        newspaper.copyPapersToDB = MagicMock()
        filename = os.path.join(here, "data/newspaper_codes")
        with open(filename) as f:
            paperCodes = f.read().splitlines()
        newspaper.sendTheseGallicaPapersToDB(paperCodes)
        self.assertEqual(
            len(newspaper.paperRecords),
            len(paperCodes)
        )
        assert newspaper.copyPapersToDB.called

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_fetched_paper_record_validity(self, mock_get):
        with open(os.path.join(here, 'data/20PaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        newspaper = Newspaper()
        newspaper.copyPapersToDB = MagicMock()
        with open(os.path.join(here, "data/newspaper_codes")) as f:
            paperCodes = f.read().splitlines()
        newspaper.sendTheseGallicaPapersToDB(paperCodes)

        for paperRecord in newspaper.paperRecords:
            self.assertIsInstance(paperRecord.paperCode, str)
            self.assertIsInstance(paperRecord.title, str)
            self.assertIsInstance(paperRecord.publishingRange, list)
            self.assertIsInstance(paperRecord.continuousRange, bool)
            self.assertIsInstance(paperRecord.url, str)

        assert newspaper.copyPapersToDB.called

    def test_fetch_papers_data_in_batches(self):

        def boomerangBatchForTesting(batchItems):
            return batchItems

        Newspaper.fetchTheseMax20PaperRecords = MagicMock(
            side_effect=boomerangBatchForTesting)
        with open(os.path.join(here, "data/newspaper_codes")) as f:
            paperCodes = f.read().splitlines()
        newspaper = Newspaper()
        newspaper.fetchPapersDataInBatches(paperCodes)
        self.assertListEqual(
            newspaper.paperRecords,
            paperCodes
        )

    def test_copy_papers_to_db(self):
        self.fail()


    # TODO: mock paperrecords better
    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_generate_csv_stream(self, mock_get):
        with open(os.path.join(here, 'data/20PaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        with open(os.path.join(here, "data/newspaper_codes")) as f:
            paperCodes = f.read().splitlines()
        newspaper = Newspaper()
        newspaper.sendTheseGallicaPapersToDB(paperCodes)

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_num_papers(self, mock_get):
        with open(os.path.join(here, 'data/dummyNewspaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        newspaper = Newspaper()
        numPapers = newspaper.getNumPapersOnGallica()
        self.assertEqual(numPapers, 18509)


