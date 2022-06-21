from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.recordBatch import RecordBatch
from gallica.recordBatch import KeywordRecordBatch
from gallica.recordBatch import PaperRecordBatch
from gallica.gallicaSession import GallicaSession

import os

from record import KeywordRecord

here = os.path.dirname(__file__)


class TestRecordBatch(TestCase):

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_get_num_results(self, mock_get):
        with open(os.path.join(here, 'data/dummyKeywordRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        batch = RecordBatch(
            '',
            GallicaSession().getSession()
        )
        self.assertEqual(batch.getNumResults(), 78514)

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_fetch_xml(self, mock_get):
        with open(os.path.join(here, 'data/dummyKeywordRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        batch = RecordBatch(
            '',
            GallicaSession().getSession()
        )

        batch.fetchXML()

        self.assertIsNotNone(batch.xmlRoot)


class TestPaperRecordBatch(TestCase):

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_parse_records_from_xml(self, mock_get):
        with open(os.path.join(here, 'data/dummyNewspaperRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())

        batch = PaperRecordBatch(
            '',
            GallicaSession().getSession()
        )

        batch.fetchXML()

        with open(os.path.join(here, 'data/continuousDateFetch.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())

        batch.parseRecordsFromXML()

        self.assertEqual(len(batch.batch), 14)
        self.assertEqual(batch.numPurgedResults, 1)


class TestKeywordRecordBatch(TestCase):

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_parse_records_from_xml(self, mock_get):
        with open(os.path.join(here, 'data/dummyKeywordRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())

        batch = KeywordRecordBatch(
            '',
            GallicaSession().getSession()
        )

        batch.fetchXML()
        batch.parseRecordsFromXML()

        self.assertEqual(len(batch.batch), 4)
        self.assertEqual(batch.numPurgedResults, 2)

    def test_record_is_unique(self):
        batch = KeywordRecordBatch(
            '',
            GallicaSession().getSession()
        )
        batch.currentResultEqualsPrior = MagicMock(return_value=True)
        self.assertTrue(batch.recordIsUnique(None))
        batch.batch = ['test']
        self.assertFalse(batch.recordIsUnique(None))
        batch.currentResultEqualsPrior = MagicMock(return_value=False)
        self.assertTrue(batch.recordIsUnique(None))

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_current_result_equals_prior(self, mock_get):
        with open(os.path.join(here, 'data/dummyKeywordRecords.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())

        batch = KeywordRecordBatch(
            '',
            GallicaSession().getSession())

        batch.fetchXML()
        self.assertCountEqual(batch.batch, [])
        xmlWithDuplicateEndCouple = [xml for xml in batch.xmlRoot.iter(
            "{http://www.loc.gov/zing/srw/}record")]
        secondToLastRecord = KeywordRecord(xmlWithDuplicateEndCouple[-2])
        lastRecord = KeywordRecord(xmlWithDuplicateEndCouple[-1])

        self.assertTrue(batch.recordIsUnique(secondToLastRecord))
        batch.batch.append(secondToLastRecord)
        self.assertFalse(batch.recordIsUnique(lastRecord))
