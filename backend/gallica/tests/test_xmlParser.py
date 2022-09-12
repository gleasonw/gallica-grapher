from unittest import TestCase
from backend.gallica.xmlParser import XMLParser
import os
from lxml import etree
from date import Date


class TestXMLParser(TestCase):

    def setUp(self) -> None:
        here = os.path.dirname(__file__)
        self.xmlParser = XMLParser(Date)
        with open(os.path.join(here, 'resources/dummyNewspaperRecords.xml'), 'rb') as f:
            self.paperXML = etree.fromstring(f.read())
        with open(os.path.join(here, 'resources/dummyOccurrenceRecords.xml'), 'rb') as f:
            self.occurrenceXML = etree.fromstring(f.read())
        with open(os.path.join(here, 'resources/dummyIssues.xml'), 'rb') as f:
            self.issuesXML = etree.fromstring(f.read())
        self.paperRecords = [
            root[2][0]
            for root in self.paperXML.iter("{http://www.loc.gov/zing/srw/}record")
        ]
        self.occurrenceRecords = [
            root[2][0]
            for root in self.occurrenceXML.iter("{http://www.loc.gov/zing/srw/}record")
        ]

    def test_getPaperCode_given_occurrence_records(self):
        paperCodes = []
        for record in self.occurrenceRecords:
            self.xmlParser.setXML(record)
            paperCode = self.xmlParser.getPaperCode()
            paperCodes.append(paperCode)
        self.assertListEqual(
            paperCodes,
            ['cb32860483w', 'cb328263310', None, 'cb328696274', 'cb32896241g', 'cb32896241g']
        )

    def test_getPaperCode_given_newspaper_records(self):
        paperCodes = []
        for record in self.paperRecords:
            self.xmlParser.setXML(record)
            paperCode = self.xmlParser.getPaperCode()
            paperCodes.append(paperCode)
        self.assertListEqual(
            paperCodes,
            [
                'cb32699739p',
                'cb339033288',
                'cb387197736',
                'cb386884277',
                'cb45393119z',
                'cb416530906',
                'cb38725602n',
                'cb45382243n',
                'cb34349269z',
                'cb452696206',
                None,
                'cb32686697n',
                'cb370153624',
                'cb45266005x',
                'cb45393434p'
            ]
        )

    def test_getURL_given_occurrence_records(self):
        urls = []
        for record in self.occurrenceRecords:
            self.xmlParser.setXML(record)
            url = self.xmlParser.getURL()
            urls.append(url)
        self.assertEqual(
            urls[4],
            'https://gallica.bnf.fr/ark:/12148/bpt6k969388g'
        )

    def test_getURL_given_newspaper_records(self):
        urls = []
        for record in self.paperRecords:
            self.xmlParser.setXML(record)
            url = self.xmlParser.getURL()
            urls.append(url)
        self.assertEqual(
            urls[4],
            'https://gallica.bnf.fr/ark:/12148/cb45393119z/date'
        )

    def test_getPaperTitle_given_newspaper_records(self):
        titles = []
        for record in self.paperRecords:
            self.xmlParser.setXML(record)
            title = self.xmlParser.getPaperTitle()
            titles.append(title)
        self.assertEqual(
            titles[4],
            "Les Échos (Secours populaire Français)"
        )

    def test_getPaperTitle_given_occurrence_records(self):
        titles = []
        for record in self.occurrenceRecords:
            self.xmlParser.setXML(record)
            title = self.xmlParser.getPaperTitle()
            titles.append(title)
        self.assertEqual(
            titles[4],
            "L'Indépendant de Boulogne-sur-Mer. Supplément illustré"
        )

    def test_getDate_given_occurrence_records(self):
        dates = []
        for record in self.occurrenceRecords:
            self.xmlParser.setXML(record)
            date = self.xmlParser.getDate()
            dates.append(date)
        self.assertListEqual(
            dates[4].getDate(),
            Date('1892').getDate()
        )

    def test_getNumRecords_given_occurrence_records(self):
        self.xmlParser.setXML(self.occurrenceXML)

        numRecords = self.xmlParser.getNumRecords()

        self.assertEqual(numRecords, 78514)

    def test_getYearsPublished_given_ark_XML(self):
        self.xmlParser.setXML(self.issuesXML)

        yearsPublished = [year for year in self.xmlParser.getYearsPublished()]

        self.assertEqual(
            len(yearsPublished),
            82
        )



