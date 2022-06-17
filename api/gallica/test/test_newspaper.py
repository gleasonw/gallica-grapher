import json
from unittest import TestCase
from unittest.mock import patch, MagicMock
from gallica.newspaper import Newspaper


class TestNewspaper(TestCase):
    def test_num_papers(self):
        newspaper = Newspaper()
        self.assertEqual(newspaper.getNumPapersOnGallica(), 14189)

    def test_send_papers_to_db(self):
        newspaper = Newspaper()
        newspaper.sendAllGallicaPapersToDB()
        self.assertGreater(len(newspaper.paperRecords), 14000)
