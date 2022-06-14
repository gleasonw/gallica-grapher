from unittest import TestCase
from gallica.record import PaperRecord
from gallica.newspaper import Newspaper


class TestNewspaper(TestCase):
    def test_num_papers(self):
        newspaper = Newspaper()
        self.assertEqual(newspaper.getNumPapersOnGallica(), 14189)

    def test_get_all_papers(self):
        newspaper = Newspaper()
        newspaper.paperRecords = [

        ]
        newspaper.sendGallicaPapersToDB()
        self.assertGreater(len(newspaper.paperRecords), 14000)
