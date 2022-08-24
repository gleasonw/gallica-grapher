from unittest import TestCase
from unittest.mock import patch, MagicMock
from paperYearGraphData import PaperYearGraphData
from DBtester import DBtester


class TestPaperYearGraphData(TestCase):

    def test_create_chart_json(self):
        testChart = PaperYearGraphData()
        testChart.getPaperMetadata = MagicMock()
        testChart.countPublishingPapersInEachYear = MagicMock()
        testChart.generateYearFrequencyList = MagicMock()
        testChart.generateJSONfileForGraphing = MagicMock()

        testChart.createChartJSON()

        testChart.getPaperMetadata.assert_called_once()
        testChart.countPublishingPapersInEachYear.assert_called_once()
        testChart.generateYearFrequencyList.assert_called_once()
        testChart.generateJSONfileForGraphing.assert_called_once()

    def test_get_paper_metadata(self):
        testChart = PaperYearGraphData()
        dbTester = DBtester()

        testChart.getPaperMetadata()

        try:
            self.assertEqual(
                testChart.lowYear,
                dbTester.getEarliestContinuousPaperDate())
            self.assertEqual(
                testChart.highYear,
                dbTester.getLatestContinuousPaperDate())
            self.assertEqual(
                len(testChart.yearOccurrenceArray),
                (testChart.highYear - testChart.lowYear) + 1)
            self.assertEqual(
                len(testChart.yearRangeList),
                dbTester.getNumberContinuousPapers())
        except Exception as e:
            self.fail(e)
        finally:
            dbTester.close()

    def test_count_publishing_papers_in_each_year(self):
        testChart = PaperYearGraphData()
        testChart.yearRangeList = [(1, 2), (3, 4), (1, 2)]
        testChart.yearOccurrenceArray = [0, 0, 0, 0]
        testChart.lowYear = 1

        testChart.countPublishingPapersInEachYear()

        self.assertListEqual(
            testChart.yearOccurrenceArray,
            [2, 2, 1, 1])

    def test_generate_year_frequency_list(self):
        testChart = PaperYearGraphData()
        testChart.yearOccurrenceArray = [1, 2, 3, 4]
        testChart.lowYear = 1
        testChart.yearFreqList = []

        testChart.generateYearFrequencyList()

        self.assertListEqual(
            testChart.yearFreqList,
            [[1, 1], [2, 2], [3, 3], [4, 4]])
