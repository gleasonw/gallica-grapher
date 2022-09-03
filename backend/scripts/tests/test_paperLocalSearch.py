from unittest import TestCase
from unittest.mock import patch, MagicMock
from scripts.paperLocalSearch import PaperLocalSearch


class TestPaperLocalSearch(TestCase):

    @patch('scripts.paperLocalSearch.PSQLconn')
    def setUp(self, mock_conn) -> None:
        self.testSearch = PaperLocalSearch()

    def test_select_papers_continuous_over_range(self):
        self.testSearch.dbConnection.cursor.return_value.__enter__.return_value.execute = MagicMock()

        self.testSearch.selectPapersContinuousOverRange(1900, 2000)

        self.testSearch.dbConnection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with("""
                SELECT title, code, startdate, enddate
                    FROM papers
                    WHERE startdate <= %s
                    AND enddate >= %s
                    AND continuous;
                """, (1900, 2000,)
        )

    def test_select_papers_similar_to_keyword(self):
        self.testSearch.dbConnection.cursor.return_value.__enter__.return_value.execute = MagicMock()

        self.testSearch.selectPapersSimilarToKeyword('NiCe')

        self.testSearch.dbConnection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with("""
                SELECT title, code, startdate, enddate
                    FROM papers 
                    WHERE LOWER(title) LIKE %(paperNameSearchString)s
                    ORDER BY title DESC LIMIT 20;
            """, {'paperNameSearchString': '%' + 'nice' + '%'})

    def test_get_num_papers_in_range(self):
        self.testSearch.dbConnection.cursor.return_value.__enter__.return_value.execute = MagicMock()

        self.testSearch.getNumPapersInRange(1900, 2000)

        self.testSearch.dbConnection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with("""
                SELECT COUNT(*) FROM papers
                    WHERE startdate BETWEEN %s AND %s
                    OR enddate BETWEEN %s AND %s;
                """, (1900, 2000, 1900, 2000))
