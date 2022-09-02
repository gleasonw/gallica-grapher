from unittest import TestCase
from unittest.mock import MagicMock, patch
from scripts.newspaper import Newspaper
import os
from DBtester import DBtester

here = os.path.dirname(__file__)


class TestNewspaper(TestCase):

    @staticmethod
    def getPaperCodes():
        with open(os.path.join(here, "resources/newspaper_codes")) as f:
            return f.read().splitlines()

    @staticmethod
    def getMockedPaperFetch():
        with open(os.path.join(here, 'resources/20PaperRecords.xml'), "rb") as f:
            return MagicMock(content=f.read())

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

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_send_these_gallica_papers_to_db(self, mock_get):
        mock_get.return_value = TestNewspaper.getMockedPaperFetch()
        paperCodes = TestNewspaper.getPaperCodes()
        tupledPaperCodes = [(code,) for code in paperCodes]
        newspaper = Newspaper()
        newspaper.copyPapersToDB = MagicMock()
        newspaper.fetchRecordDataForCodes = MagicMock()

        newspaper.sendTheseGallicaPapersToDB(tupledPaperCodes)

        newspaper.copyPapersToDB.assert_called_once()
        newspaper.fetchRecordDataForCodes.assert_called_with(tupledPaperCodes)

    @patch('scripts.newspaper.PSQLconn')
    @patch('scripts.newspaper.Newspaper.fetchAllPapersFromGallica')
    @patch('scripts.newspaper.Newspaper.copyPapersToDB')
    def test_send_all_gallica_papers_to_db(self, mock_copy, mock_fetch, mock_db):
        mock_db.return_value = mock_db
        mock_db.getConn.return_value = mock_db
        mock_db.close = MagicMock()
        newspaper = Newspaper(MagicMock())

        newspaper.fetchAllPaperRecordsOnGallica()

        self.assertEqual(
            'dc.type all "fascicule" and ocrquality > "050.00"',
            newspaper.query
        )
        mock_copy.assert_called_once()
        mock_fetch.assert_called_once()
        mock_db.close.assert_called_once()

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_fetched_paper_record_validity(self, mock_get):
        with open(os.path.join(here, 'resources/20PaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        newspaper = Newspaper()
        newspaper.copyPapersToDB = MagicMock()
        with open(os.path.join(here, "resources/newspaper_codes")) as f:
            paperCodes = f.read().splitlines()
        newspaper.sendTheseGallicaPapersToDB(paperCodes)

        for paperRecord in newspaper.paperRecords:
            self.assertIsInstance(paperRecord.paperCode, str)
            self.assertIsInstance(paperRecord.paperTitle, str)
            self.assertIsInstance(paperRecord.publishingRange, list)
            self.assertIsInstance(paperRecord.continuousRange, bool)
            self.assertIsInstance(paperRecord.url, str)

        assert newspaper.copyPapersToDB.called

    def test_fetch_papers_data_in_batches(self):
        def boomerangBatchForTesting(batchItems):
            return [i for i in range(len(batchItems))]

        paperCodes20 = TestNewspaper.getPaperCodes()
        newspaper = Newspaper(MagicMock())
        newspaper.fetchTheseMax20PaperRecords = MagicMock(
            side_effect=boomerangBatchForTesting
        )

        newspaper.fetchRecordDataForCodes(paperCodes20)

        self.assertEqual(
            len(newspaper.paperRecords),
            len(paperCodes20)
        )

        oneMissingPaper = Newspaper(MagicMock())
        oneMissingPaper.fetchTheseMax20PaperRecords = MagicMock(
            side_effect=boomerangBatchForTesting)
        oneMissingPaper.fetchRecordDataForCodes(["12345"])

        self.assertEqual(
            len(oneMissingPaper.paperRecords),
            1
        )

    @patch('record.PaperRecord')
    @patch('record.Record')
    def test_generate_csv_stream(self, mock_record, mock_paper_record):
        newspaper = Newspaper()
        mock_record.return_value = mock_record
        mock_paper_record.return_value = mock_paper_record
        mock_record.parsePaperCodeFromXML = MagicMock(return_value="123")
        mock_record.parseURLFromXML = MagicMock(return_value="http://example.com")
        mock_paper_record.checkIfValid = MagicMock(return_value=True)
        mock_paper_record.parseTitleFromXML = MagicMock(return_value="title")
        mock_paper_record.fetchYearsPublished = MagicMock(return_value=["range"])
        mock_paper_record.parseYears = MagicMock(return_value=["range"])
        mock_paper_record.checkIfYearsContinuous = MagicMock(return_value=True)
        mock_paper_record.generatePublishingRange = MagicMock(return_value=["range"])
        mock_paper_record.getDate = MagicMock(return_value=[1, 2])
        mock_paper_record.getPaperTitle = MagicMock(return_value="title")
        mock_paper_record.isContinuous = MagicMock(return_value=True)
        mock_paper_record.getPaperCode = MagicMock(return_value="123")

        newspaper.paperRecords = [mock_paper_record for i in range(20)]

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
        with open(os.path.join(here, 'resources/dummyNewspaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        newspaper = Newspaper()
        numPapers = newspaper.getNumPapersOnGallica()
        self.assertEqual(numPapers, 18509)

    @patch('scripts.newspaper.GallicaPaperRecordBatch')
    def test_fetch_max_20_paper_records(self, mock_paper_record_batch):
        mock_paper_record_batch.return_value = mock_paper_record_batch
        mock_paper_record_batch.getRecords = MagicMock(return_value=[])
        testCodes = TestNewspaper.getPaperCodes()

        newspaper = Newspaper()
        newspaper.fetchTheseMax20PaperRecords(testCodes)

        self.assertEqual(len(newspaper.paperRecords), 0)
