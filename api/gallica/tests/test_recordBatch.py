from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.recordBatch import RecordBatch
from gallica.recordBatch import KeywordRecordBatch
from gallica.recordBatch import PaperRecordBatch
from gallica.gallicaSession import GallicaSession

import os

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
        self.fail()

    def test_current_result_equals_prior(self):
        self.fail()
