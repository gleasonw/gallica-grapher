from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.keywordQuery import KeywordQueryAllPapers
from gallica.keywordQuery import KeywordQuerySelectPapers


class TestKeywordQuery(TestCase):

    def test_post_results(self):
        pass

    def test_get_results_all_papers_keyword(self):
        query = KeywordQueryAllPapers(
            "brazza",
            [1850, 1900],
            '43211',
            MagicMock(),
            MagicMock(),
        )

    def test_get_results_some_papers_keyword(self):
        query = KeywordQuerySelectPapers(
            "brazza",
            [1850, 1900],
            '43211',
            MagicMock(),
            MagicMock(),
        )



