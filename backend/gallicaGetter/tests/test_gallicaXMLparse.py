from unittest import TestCase
from gallicaxmlparse import GallicaXMLparse
from date import Date
import os

here = os.path.dirname(os.path.abspath(__file__))


class TestGallicaXMLparse(TestCase):

    def setUp(self) -> None:
        self.parse = GallicaXMLparse()
        with open(os.path.join(here, 'xmlForTesting/occurrences.xml'), 'rb') as f:
            self.occurrencesXML = f.read()
        with open(os.path.join(here, 'xmlForTesting/papers.xml'), 'rb') as f:
            self.papersXML = f.read()
        with open(os.path.join(here, 'xmlForTesting/issues.xml'), 'rb') as f:
            self.issuesXML = f.read()
        with open(os.path.join(here, 'xmlForTesting/ocrText.xml'), 'rb') as f:
            self.ocrTextXML = f.read()

    def test_get_one_paper_from_record_batch(self):
        self.assertEqual(
            self.parse.getOnePaperFromRecordBatch(self.occurrencesXML),
            'Revue maritime et coloniale / Ministère de la marine et des colonies'
        )

    def test_get_num_results_and_pages_for_occurrence_in_periodical(self):
        countAndResults = self.parse.getNumResultsAndPagesForOccurrenceInPeriodical(self.ocrTextXML)
        self.assertEqual(countAndResults[0], '364')
        self.assertEqual(len(countAndResults[1]), 5)

    def test_get_records_from_xml(self):
        test = self.parse.getRecordsFromXML(self.occurrencesXML)
        self.assertEqual(len(test), 6)

    def test_get_num_records(self):
        self.assertEqual(
            self.parse.getNumRecords(self.occurrencesXML),
            78514
        )

    def test_get_years_published(self):
        self.assertEqual(
            self.parse.getYearsPublished(self.issuesXML),
            list(str(year) for year in range(1861,1943))
        )

    def test_get_paper_code(self):
        records = self.parse.getRecordsFromXML(self.papersXML)
        oneRecord = records[0]
        self.assertEqual(
            self.parse.getPaperCodeFromRecord(oneRecord),
            'cb32699739p'
        )

    def test_get_url(self):
        records = self.parse.getRecordsFromXML(self.occurrencesXML)
        oneRecord = records[0]
        self.assertEqual(
            self.parse.getURLfromRecord(oneRecord),
            'https://gallica.bnf.fr/ark:/12148/bpt6k34565h'
        )

    def test_get_paper_title(self):
        records = self.parse.getRecordsFromXML(self.papersXML)
        oneRecord = records[0]
        self.assertEqual(
            self.parse.getPaperTitleFromRecord(oneRecord),
            "L'Anti-cafard. Revue anti-boche, publiée très irrégulièrement avec le concours de toutes les bonnes volontés"
        )

    def test_get_date(self):
        records = self.parse.getRecordsFromXML(self.occurrencesXML)
        oneRecord = records[0]
        self.assertListEqual(
            self.parse.getDateFromRecord(oneRecord).getDateAsList(),
            Date('1883-04').getDateAsList()
        )