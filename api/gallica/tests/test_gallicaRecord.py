from unittest import TestCase
from unittest.mock import MagicMock, patch
from lxml import etree
import os
from gallica.gallicaRecord import GallicaRecord
from gallica.gallicaRecord import GallicaKeywordRecord
from gallica.gallicaRecord import GallicaPaperRecord
from gallica.gallicaSession import GallicaSession


class TestRecord(TestCase):

    def test_parse_paper_code_from_xml(self):
        here = os.path.dirname(__file__)
        dummyRoot = etree.parse(os.path.join(here, 'resources/dummyNewspaperRecords.xml'))
        dummyRecordXML = dummyRoot.find('{http://www.loc.gov/zing/srw/}records')
        dummyRecordXML = dummyRecordXML.find('{http://www.loc.gov/zing/srw/}record')
        dummyRecord = GallicaRecord(dummyRecordXML)

        self.assertEqual(
            dummyRecord.getPaperCode(),
            'cb32699739p')

    def test_parse_urlfrom_xml(self):
        here = os.path.dirname(__file__)
        dummyRoot = etree.parse(os.path.join(here, 'resources/dummyNewspaperRecords.xml'))
        dummyRecordXML = dummyRoot.find('{http://www.loc.gov/zing/srw/}records')
        dummyRecordXML = dummyRecordXML.find('{http://www.loc.gov/zing/srw/}record')
        dummyRecord = GallicaRecord(dummyRecordXML)

        self.assertEqual(
            dummyRecord.getUrl(),
            'https://gallica.bnf.fr/ark:/12148/cb32699739p/date')

    def test_check_if_valid(self):
        here = os.path.dirname(__file__)
        dummyRoot = etree.parse(os.path.join(here, 'resources/dummyKeywordRecords.xml'))
        dummys = dummyRoot.find('{http://www.loc.gov/zing/srw/}records')
        malformedDateRecord = GallicaKeywordRecord(dummys[1])
        absentCodeRecord = GallicaKeywordRecord(dummys[2])

        self.assertTrue(malformedDateRecord.isValid())
        self.assertFalse(absentCodeRecord.isValid())


class TestPaperRecord(TestCase):
    def test_check_if_valid(self):
        here = os.path.dirname(__file__)
        dummyRoot = etree.parse(os.path.join(here, 'resources/dummyNewspaperRecords.xml'))
        dummyRecordXML = dummyRoot.find('{http://www.loc.gov/zing/srw/}records')
        firstRecord = dummyRecordXML.find('{http://www.loc.gov/zing/srw/}record')

        with patch.object(GallicaPaperRecord, 'fetchYearsPublished', return_value=None) as mock_fetch_published:
            paperRecord = GallicaPaperRecord(firstRecord, MagicMock)

        self.assertTrue(paperRecord.isValid())

    @patch('requests_toolbelt.sessions.BaseUrlSession.get')
    def test_fetch_years_published(self, mock_get):
        here = os.path.dirname(__file__)
        with open(os.path.join(here, 'resources/continuousDateFetch.xml'), "rb") as f:
            mock_get.return_value = MagicMock(content=f.read())
        dummyRoot = etree.parse(os.path.join(here, 'resources/dummyNewspaperRecords.xml'))
        dummyRecordXML = dummyRoot.find('{http://www.loc.gov/zing/srw/}records')
        firstRecord = dummyRecordXML.find('{http://www.loc.gov/zing/srw/}record')
        paperRecord = GallicaPaperRecord(firstRecord, GallicaSession().getSession())

        self.assertEqual(
            paperRecord.getDate(),
            [1916, 1916]
        )

    def test_check_if_years_continuous(self):
        here = os.path.dirname(__file__)
        dummyRoot = etree.parse(os.path.join(here, 'resources/dummyNewspaperRecords.xml'))
        dummyRecordXML = dummyRoot.find('{http://www.loc.gov/zing/srw/}records')
        dummyRecordXML = dummyRecordXML.find('{http://www.loc.gov/zing/srw/}record')

        with patch.object(GallicaPaperRecord, 'fetchYearsPublished', return_value=None) as mock_fetch_published:
            continuousPaperRecord = GallicaPaperRecord(dummyRecordXML, MagicMock)
            sporadicPaperRecord = GallicaPaperRecord(dummyRecordXML, MagicMock)
            continuousPaperRecord.publishingYears = [1918, 1919, 1920]
            sporadicPaperRecord.publishingYears = [1918, 1919, 2020, 2021]
            continuousPaperRecord.checkIfYearsContinuous()
            sporadicPaperRecord.checkIfYearsContinuous()

        self.assertTrue(continuousPaperRecord.isContinuous())
        self.assertFalse(sporadicPaperRecord.isContinuous())

    def test_generate_available_range(self):
        here = os.path.dirname(__file__)
        dummyRoot = etree.parse(os.path.join(here, 'resources/dummyNewspaperRecords.xml'))
        dummyRecordXML = dummyRoot.find('{http://www.loc.gov/zing/srw/}records')
        dummyRecordXML = dummyRecordXML.find('{http://www.loc.gov/zing/srw/}record')

        with patch.object(GallicaPaperRecord, 'fetchYearsPublished', return_value=None) as mock_fetch_published:
            continuousPaperRecord = GallicaPaperRecord(dummyRecordXML, MagicMock)
            sporadicPaperRecord = GallicaPaperRecord(dummyRecordXML, MagicMock)
            continuousPaperRecord.publishingYears = [1918, 1919, 1920]
            sporadicPaperRecord.publishingYears = [1918, 1919, 2020, 2021]
            continuousPaperRecord.generatePublishingRange()
            sporadicPaperRecord.generatePublishingRange()

        self.assertEqual(
            continuousPaperRecord.publishingRange,
            [1918, 1920]
        )
        self.assertEqual(
            sporadicPaperRecord.publishingRange,
            [1918, 2021]
        )

    def test_parse_title_from_xml(self):
        here = os.path.dirname(__file__)
        dummyRoot = etree.parse(os.path.join(here, 'resources/dummyNewspaperRecords.xml'))
        dummyRecordXML = dummyRoot.find('{http://www.loc.gov/zing/srw/}records')
        dummyRecordXML = dummyRecordXML.find('{http://www.loc.gov/zing/srw/}record')

        with patch.object(GallicaPaperRecord, 'fetchYearsPublished', return_value=None) as mock_fetch_published:
            record = GallicaPaperRecord(dummyRecordXML, MagicMock)

        self.assertEqual(
            record.getPaperTitle(),
            "L'Anti-cafard. Revue anti-boche, publiée très irrégulièrement avec le concours de toutes les bonnes volontés"
        )
