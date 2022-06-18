from unittest import TestCase
from unittest.mock import MagicMock
from gallica.newspaper import Newspaper
import os

here = os.path.dirname(__file__)


class TestNewspaper(TestCase):

    def test_fetch_record_data_from_code_strings(self):
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

    def test_fetched_paper_record_validity(self):
        newspaper = Newspaper()
        newspaper.copyPapersToDB = MagicMock()
        filename = os.path.join(here, "data/newspaper_codes")
        with open(filename) as f:
            paperCodes = f.read().splitlines()
        newspaper.sendTheseGallicaPapersToDB(paperCodes)

        for paperRecord in newspaper.paperRecords:
            self.assertIsInstance(paperRecord.paperCode, str)
            self.assertIsInstance(paperRecord.title, str)
            self.assertIsInstance(paperRecord.publishingRange, list)
            self.assertIsInstance(paperRecord.continuousRange, bool)
            self.assertIsInstance(paperRecord.url, str)

        assert newspaper.copyPapersToDB.called

# TODO: Create a table with our codes, delete them, then check if they are back in after running the function
    def test_copy_papers_to_db(self):
        self.fail()

    def test_num_papers(self):
        newspaper = Newspaper()
        self.assertEqual(newspaper.getNumPapersOnGallica(), 14189)


