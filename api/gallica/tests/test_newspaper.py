from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.newspaper import Newspaper
from gallica.record import Record, PaperRecord
import os
from lxml import etree
from DBtester import DBtester

here = os.path.dirname(__file__)


class TestNewspaper(TestCase):

    @staticmethod
    def getMockedPaperFetch():
        with open(os.path.join(here, 'data/20PaperRecords.xml'), "rb") as f:
            return MagicMock(content=f.read())

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_send_these_gallica_papers_to_db(self, mock_get):
        mock_get.return_value = TestNewspaper.getMockedPaperFetch()
        with open(os.path.join(here, "data/newspaper_codes")) as f:
            paperCodes = f.read().splitlines()

        newspaper = Newspaper()
        newspaper.copyPapersToDB = MagicMock()
        newspaper.fetchPapersDataInBatches = MagicMock()

        newspaper.sendTheseGallicaPapersToDB(paperCodes)

        newspaper.copyPapersToDB.assert_called_once()
        newspaper.fetchPapersDataInBatches.assert_called_with(paperCodes)

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
            return [i for i in range(len(batchItems))]

        with open(os.path.join(here, "data/newspaper_codes")) as f:
            paperCodes = f.read().splitlines()

        newspaper = Newspaper(MagicMock())
        newspaper.fetchTheseMax20PaperRecords = MagicMock(
            side_effect=boomerangBatchForTesting
        )

        newspaper.fetchPapersDataInBatches(paperCodes)

        self.assertEqual(
            len(newspaper.paperRecords),
            len(paperCodes)
        )

    def test_copy_papers_to_db(self):
        testerPaper = Newspaper()
        mockPaperRecords = [
            MagicMock(
                getDate=MagicMock(return_value=[1800,1900]),
                getTitle=MagicMock(return_value='test1'),
                isContinuous=MagicMock(return_value=True),
                getPaperCode=MagicMock(return_value='12345')),
            MagicMock(
                getDate=MagicMock(return_value=[1899,1900]),
                getTitle=MagicMock(return_value='test2'),
                isContinuous=MagicMock(return_value=False),
                getPaperCode=MagicMock(return_value='54321')),
        ]
        testerPaper.paperRecords = mockPaperRecords

        testerPaper.copyPapersToDB()

        firstPaper = DBtester().deleteAndReturnPaper('12345')
        secondPaper = DBtester().deleteAndReturnPaper('54321')

        self.assertEqual(
            firstPaper,
            '(test1,1800,1900,t,12345)'
        )
        self.assertEqual(
            secondPaper,
            '(test2,1899,1900,f,54321)'
        )


        pass

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
        mock_paper_record.getDate = MagicMock(return_value=[1,2])
        mock_paper_record.getTitle = MagicMock(return_value="title")
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
        with open(os.path.join(here, 'data/dummyNewspaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        newspaper = Newspaper()
        numPapers = newspaper.getNumPapersOnGallica()
        self.assertEqual(numPapers, 18509)


