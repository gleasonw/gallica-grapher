import unittest
from paperRecord import PaperRecord


class TestPaperRecord(unittest.TestCase):

    def setUp(self) -> None:
        self.testPaperRecord = PaperRecord(
            code='testCode',
            title='testTitle',
            url='testUrl'
        )

    def test_getRowContinuousYears(self):
        self.testPaperRecord.addYearsFromArk(['1900', '1901', '1902'])

        self.assertEqual(
            self.testPaperRecord.getRow(),
            (
                'testTitle',
                '1900',
                '1902',
                True,
                'testCode'
            )
        )

    def test_getRowNonContinuousYears(self):
        self.testPaperRecord.addYearsFromArk(['1900', '1901', '1903'])

        self.assertEqual(
            self.testPaperRecord.getRow(),
            (
                'testTitle',
                '1900',
                '1903',
                False,
                'testCode'
            )
        )


if __name__ == '__main__':
    unittest.main()
