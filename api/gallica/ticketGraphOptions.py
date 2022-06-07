import json
import psycopg2
from .ticketGraphSeries import TicketGraphSeries
import itertools

class TicketGraphOptions:
    def __init__(self,
                 requestids,
                 averagewindow=0,
                 groupby='day'):

        self.dbConnection = None
        self.requestIDs = requestids
        self.averageWindow = int(averagewindow)
        self.groupBy = groupby
        self.dataBatches = []
        self.categories = []
        self.mappedSeries = []
        self.options = {}
        self.lowYear = None
        self.highYear = None

        self.initDBConnection()
        self.selectGraphSeries()

    def getOptions(self):
        return self.options

    def selectGraphSeries(self):
        self.dataBatches = list(map(self.selectDataForRequestID, self.requestIDs))
        self.generateOptions()
        self.dbConnection.close()

    def selectDataForRequestID(self, requestID):
        series = TicketGraphSeries(
            requestID,
            self.dbConnection,
            self.averageWindow,
            self.groupBy)
        return series.getSeries()

    def generateOptions(self):
        if self.groupBy in ['month', 'year']:
            self.generateCategoriesForHighcharts()

    def generateCategoriesForHighcharts(self):
        self.lowYear = self.getLowestYear()
        self.highYear = self.getHighestYear()
        if self.groupBy == 'month':
            self.createMonthCategories()
            self.indexYearMonthBatches()
        else:
            self.createYearCategories()
            self.mapYearsToCategoryIndex()

    def createMonthCategories(self):
        def gen12MonthsInYear(year):
            return list(map(
                lambda month: f'{year}/{month}',
                range(1, 13)
            ))

        self.categories = list(map(
            gen12MonthsInYear,
            range(self.lowYear, self.highYear + 1)))
        self.categories = itertools.chain.from_iterable(self.categories)

    def createYearCategories(self):
        self.categories = [int(i) for i in range(self.lowYear, self.highYear + 1)]

    def getLowestYear(self):
        lowYears = list(map(
            lambda batch: int(batch[0][0]),
            self.dataBatches))
        return min(lowYears)

    def getHighestYear(self):
        highYears = list(map(
            lambda batch: int(batch[-1][0]),
            self.dataBatches))
        return max(highYears)

    def indexYearMonthBatches(self):
        
        def indexYearMonthBatch(batch):

            def indexYearMonthRecord(record):
                year = record[0]
                month = record[1]
                freq = record[-1]
                index = (year - self.lowYear) + (month - 1)
                return {
                    'x': int(index),
                    'y': freq
                }
            return list(map(
                indexYearMonthRecord,
                batch
            ))

        self.mappedSeries = list(map(
            indexYearMonthBatch,
            self.dataBatches
        ))

    def mapYearsToCategoryIndex(self):
        
        def mapYearsOfBatch(batch):
            return list(map(
                indexYearRecord,
                batch
            ))

        self.mappedSeries = list(map(
            mapYearsOfBatch,
            self.dataBatches
        ))

    def initDBConnection(self):
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        self.dbConnection = conn



