from unittest import TestCase

from gallicaGetter.fetch.paperQuery import PaperQuery


class TestPaperQuery(TestCase):

    def setUp(self) -> None:
        self.paperQuery = PaperQuery(
            start_index=0,
            num_records=10,
            endpoint='test'
        )
        self.selectPaperQuery = PaperQuery(
            start_index=0,
            num_records=10,
            endpoint='test',
            codes=['test', 'neat']
        )

    def test_get_cql_all_papers(self):
        self.assertEqual(
            self.paperQuery.cql,
            "dc.type all \"fascicule\" and ocr.quality all \"Texte disponible\""
        )

    def test_get_cql_some_papers(self):
        self.assertEqual(
            self.selectPaperQuery.cql,
            "arkPress adj \"test_date\" or arkPress adj \"neat_date\""
        )
