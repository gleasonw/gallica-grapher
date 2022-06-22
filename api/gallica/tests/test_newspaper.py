from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.newspaper import Newspaper
from gallica.record import Record, PaperRecord
import os
from lxml import etree

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

        with open(os.path.join(here, "data/newspaper_codes")) as f:
            paperCodes = f.read().splitlines()
        newspaper = Newspaper()
        newspaper.fetchTheseMax20PaperRecords = MagicMock(
            side_effect=boomerangBatchForTesting)
        newspaper.fetchPapersDataInBatches(paperCodes)
        self.assertListEqual(
            newspaper.paperRecords,
            paperCodes
        )

    def test_copy_papers_to_db(self):
        self.fail()

    # TODO: use patches instead of explicit mocking
    def test_generate_csv_stream(self):
        newspaper = Newspaper()
        Record.parsePaperCodeFromXML = MagicMock(return_value="123")
        Record.parseURLFromXML = MagicMock(return_value="http://example.com")
        PaperRecord.checkIfValid = MagicMock(return_value=True)
        PaperRecord.parseTitleFromXML = MagicMock(return_value="title")
        PaperRecord.fetchYearsPublished = MagicMock(return_value=["range"])
        PaperRecord.parseYears = MagicMock(return_value=["range"])
        PaperRecord.checkIfYearsContinuous = MagicMock(return_value=True)
        PaperRecord.generatePublishingRange = MagicMock(return_value=["range"])
        PaperRecord.getDate = MagicMock(return_value=[1,2])
        PaperRecord.getTitle = MagicMock(return_value="title")
        PaperRecord.isContinuous = MagicMock(return_value=True)
        PaperRecord.getPaperCode = MagicMock(return_value="123")

        newspaper.paperRecords = [PaperRecord([None,None,[None]], None) for i in range(20)]

        testCSVstream = newspaper.generateCSVstream()
        streamRows = testCSVstream.getvalue().split("\n")
        firstStreamRow = streamRows[0].split("|")

        self.assertEqual(
            len(streamRows),
            21)
        self.assertEqual(
            firstStreamRow[0],
            "title")
        self.assertEqual(
            firstStreamRow[1],
            '1')
        self.assertEqual(
            firstStreamRow[2],
            '2')
        self.assertEqual(
            firstStreamRow[3],
            'True')
        self.assertEqual(
            firstStreamRow[4],
            "123")

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_num_papers(self, mock_get):
        with open(os.path.join(here, 'data/dummyNewspaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        newspaper = Newspaper()
        numPapers = newspaper.getNumPapersOnGallica()
        self.assertEqual(numPapers, 18509)


