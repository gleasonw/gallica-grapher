from unittest import TestCase
from gallicaGetter.buildqueries.buildIssueQueries import build_issue_queries_for_codes
from gallicaGetter.fetch.issueQuery import IssueQueryForNewspaperYears


class Test(TestCase):
    def test_build_issue_queries_for_codes(self):
        result = build_issue_queries_for_codes('test', 'test')
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], IssueQueryForNewspaperYears)