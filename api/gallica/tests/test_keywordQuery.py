from unittest import TestCase
from unittest.mock import MagicMock, patch
from gallica.gallicaSession import GallicaSession
from gallica.keywordQuery import KeywordQuery
from gallica.keywordQuery import KeywordQueryAllPapers
from gallica.keywordQuery import KeywordQuerySelectPapers
import os

here = os.path.dirname(__file__)
class TestKeywordQuery(TestCase):

    def test_post_results(self):
        self.fail()

    def test_post_missing_papers(self):
        self.fail()

    def test_move_results_to_final(self):
        self.fail()

    def test_establish_year_range(self):
        self.fail()

    def test_build_query(self):
        self.fail()


class TestKeywordQueryAllPapers(TestCase):

    def test_find_num_results_for_settings(self):
        self.fail()

    def test_build_year_range_query(self):
        KeywordQueryAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = KeywordQueryAllPapers(
            'brazza',
            [1850,1900],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQuery,
            'dc.date >= "1850" and dc.date <= "1900" '
            'and (gallica all "brazza") '
            'and (dc.type all "fascicule") '
            'sortby dc.date/sort.ascending')

    def test_build_dateless_query(self):
        KeywordQueryAllPapers.fetchNumTotalResults = MagicMock(return_value=3)

        query = KeywordQueryAllPapers(
            'brazza',
            [],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=MagicMock()
        )

        self.assertEqual(
            query.baseQuery,
            '(gallica all "brazza") '
            'and (dc.type all "fascicule") '
            'sortby dc.date/sort.ascending')

    def test_fetch_num_total_results(self):

        query = KeywordQueryAllPapers(
            'brazza',
            [],
            '1234',
            progressTracker=MagicMock(),
            dbConnection=MagicMock(),
            session=GallicaSession().getSession()
        )

        self.assertEqual(query.estimateNumResults, 78514)


class TestKeywordQuerySelectPapers(TestCase):
    def test_build_year_range_query(self):
        KeywordQuerySelectPapers.fetchNumTotalResults = MagicMock(return_value=3)

        with open(os.path.join(here, "data/dummy_newspaper_choice_dicts")) as f:
            dummyNewspaperChoices = f.read().splitlines()
            choiceDict = []
            for nameCode in dummyNewspaperChoices:
                nameCode = nameCode.split(',')
                choiceDict.append(
                    {'name': nameCode[0].strip(),
                     'code': nameCode[1].strip()})

        query = KeywordQuerySelectPapers(
            'brazza',
            choiceDict,
            [1850, 1900],
            '1234',
            MagicMock(),
            MagicMock(),
            MagicMock())

        self.assertEqual(
            query.baseQuery,
            'arkPress all "{newsKey}_date" '
            'and dc.date >= "1850" '
            'and dc.date <= "1900" '
            'and (gallica all "brazza") '
            'sortby dc.date/sort.ascending')

    def test_build_dateless_query(self):
        self.fail()

    def test_set_num_results_for_each_paper(self):
        self.fail()

    def test_fetch_number_results_in_paper(self):
        self.fail()

    def test_sum_up_paper_results_for_total_estimate(self):
        self.fail()

    def test_init_batch_queries(self):
        self.fail()

    def test_append_batch_query_strings_for_paper(self):
        self.fail()
