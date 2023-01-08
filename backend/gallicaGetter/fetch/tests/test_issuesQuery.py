from unittest import TestCase
from gallicaGetter.fetch.issueQuery import IssueQueryForNewspaperYears


class TestIssuesQuery(TestCase):
    def setUp(self) -> None:
        self.arkQuery = IssueQueryForNewspaperYears(code="test", endpoint_url="test")

    def test_get_fetch_params(self):
        test = self.arkQuery.get_params_for_fetch()
        self.assertDictEqual(test, {"ark": "ark:/12148/test/date"})
