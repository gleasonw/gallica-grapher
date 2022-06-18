from unittest import TestCase
from gallica.topPapers import TopPapers


class TestTopPapers(TestCase):
    def testTopPapersContinuous(self):
        papers = TopPapers(
            '4321',
            1800,
            1900,
            continuous=True
        )
        self.assertEqual(papers.getTopPapers(),
                          [('Gazette nationale ou le Moniteur universel',285)])

    def testTopPapers(self):
        papers = TopPapers(
            '4321',
            1800,
            1900
        )
        self.assertEqual(papers.getTopPapers()[0],
                          ('Le Temps (Paris. 1861)', 723))
