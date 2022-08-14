from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.gallicaRecordBatch import GallicaRecordBatch
from gallica.gallicaRecordBatch import GallicaKeywordRecordBatch
from gallica.gallicaRecordBatch import GallicaPaperRecordBatch
from gallica.gallicaSession import GallicaSession

import os

from gallicaRecord import GallicaKeywordRecord

here = os.path.dirname(__file__)


class TestRecordBatch(TestCase):

    @staticmethod
    def get_request_mock():
        with open(os.path.join(here, 'resources/dummyKeywordRecords.xml'), "rb") as f:
            return MagicMock(content=f.read())

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_get_num_results(self, mock_get):
        mock_get.return_value = self.get_request_mock()
        batch = GallicaRecordBatch(
            '',
            GallicaSession().getSession()
        )
        self.assertEqual(batch.getNumResults(), 78514)

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_fetch_xml(self, mock_get):
        mock_get.return_value = self.get_request_mock()
        batch = GallicaRecordBatch(
            '',
            GallicaSession().getSession()
        )

        batch.fetchXML()

        self.assertEqual(
            6,
            len(batch.xmlRoot.findall(
                ".//{http://www.loc.gov/zing/srw/}record")
            ))


class TestPaperRecordBatch(TestCase):

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_parse_records_from_xml(self, mock_get):
        with open(os.path.join(here, 'resources/dummyNewspaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())

        batch = GallicaPaperRecordBatch(
            '',
            GallicaSession().getSession()
        )

        batch.fetchXML()

        with open(os.path.join(here, 'resources/continuousDateFetch.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())

        batch.parseRecordsFromXML()

        self.assertEqual(len(batch.batch), 14)
        self.assertEqual(batch.numPurgedResults, 1)


class TestKeywordRecordBatch(TestCase):

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_parse_records_from_xml(self, mock_get):
        with open(os.path.join(here, 'resources/dummyKeywordRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())

        batch = GallicaKeywordRecordBatch(
            '',
            GallicaSession().getSession()
        )

        batch.fetchXML()
        batch.parseRecordsFromXML()

        self.assertEqual(len(batch.batch), 5)
        self.assertEqual(batch.numPurgedResults, 1)

    @patch('gallica.gallicaRecordBatch.GallicaRecordBatch.fetchXML')
    def test_record_is_unique(self, mock_fetch):
        batch = GallicaKeywordRecordBatch(
            '',
            MagicMock
        )
        batch.currentResultEqualsPrior = MagicMock(return_value=True)
        self.assertTrue(batch.recordIsUnique(None))
        batch.batch = ['test']
        self.assertFalse(batch.recordIsUnique(None))
        batch.currentResultEqualsPrior = MagicMock(return_value=False)
        self.assertTrue(batch.recordIsUnique(None))

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_current_result_equals_prior(self, mock_get):
        with open(os.path.join(here, 'resources/dummyKeywordRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())

        batch = GallicaKeywordRecordBatch(
            '',
            GallicaSession().getSession())

        batch.fetchXML()
        self.assertCountEqual(batch.batch, [])
        xmlWithDuplicateEndCouple = [xml for xml in batch.xmlRoot.iter(
            "{http://www.loc.gov/zing/srw/}record")]
        secondToLastRecord = GallicaKeywordRecord(xmlWithDuplicateEndCouple[-2])
        lastRecord = GallicaKeywordRecord(xmlWithDuplicateEndCouple[-1])

        self.assertTrue(batch.recordIsUnique(secondToLastRecord))
        batch.batch.append(secondToLastRecord)
        self.assertFalse(batch.recordIsUnique(lastRecord))
