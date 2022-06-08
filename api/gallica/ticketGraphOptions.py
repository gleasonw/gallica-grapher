import datetime
import json
import psycopg2
from .ticketGraphSeries import TicketGraphSeries
import itertools
import ciso8601


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
        self.seriesCollection = []
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
        else:
            self.parseDaysIntoJSTimestamp()
        self.formatOptions()

    def generateCategoriesForHighcharts(self):
        self.lowYear = self.getLowestYear()
        self.highYear = self.getHighestYear()
        if self.groupBy == 'month':
            self.createMonthCategories()
            self.indexYearMonthBatches()
        else:
            self.createYearCategories()
            self.indexYearBatches()

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
        self.categories = [i for i in range(self.lowYear, self.highYear + 1)]

    def getLowestYear(self):
        lowYears = list(map(
            lambda batch: batch[0][0],
            self.dataBatches))
        return min(lowYears)

    def getHighestYear(self):
        highYears = list(map(
            lambda batch: batch[-1][0],
            self.dataBatches))
        return max(highYears)

    def indexYearMonthBatches(self):
        
        def indexYearMonthBatch(batch):

            def indexYearMonthRecord(record):
                year = record[0]
                month = record[1]
                freq = record[2]
                index = (year - self.lowYear) + (month - 1)
                return {
                    'x': index,
                    'y': freq
                }
            return list(map(
                indexYearMonthRecord,
                batch
            ))

        self.seriesCollection = list(map(indexYearMonthBatch, self.dataBatches))

    def indexYearBatches(self):
        
        def indexYearBatch(batch):

            def indexYearRecord(record):
                year = record[0]
                freq = record[1]
                index = year - self.lowYear
                return {
                    'x': index,
                    'y': freq
                }

            return list(map(
                indexYearRecord,
                batch
            ))

        self.seriesCollection = list(map(indexYearBatch, self.dataBatches))

    def parseDaysIntoJSTimestamp(self):

        def parseBatch(batch):

            def parseRecord(record):

                def makeDayTwoDigits(dateString):
                    dates = dateString.split('-')
                    day = dates[2]
                    if len(day) == 1:
                        dates[2] = f'0{day}'
                    return "".join(dates)

                date = makeDayTwoDigits(record[0])
                freq = record[1]
                dateObject = ciso8601.parse_datetime(date)
                timestamp = datetime.datetime.timestamp(dateObject) * 1000
                return {
                    'x': timestamp,
                    'y': freq
                }

            return list(map(parseRecord, batch))

        self.seriesCollection = list(map(parseBatch, self.dataBatches))

    def formatOptions(self):
        if self.groupBy == 'day':
            self.formatDayOptions()
        else:
            self.options = {
                'yAxis': {
                    'title': {
                        'text': 'Mentions'
                    }
                },
                'xAxis': {
                    'categories': self.categories,
                    'accessibility': {
                        'rangeDescription': f'Range: {self.lowYear} to {self.highYear}'
                    }
                },
                'series': self.seriesCollection
            }

    def formatDayOptions(self):
        self.options = {
            'yAxis': {
                'title': {
                    'text': 'Mentions'
                }
            },
            'xAxis': {
                'type': 'datetime'
            },
            'series': self.seriesCollection
        }

    def initDBConnection(self):
        conn = psycopg2.connect(
            host="localhost",
            database="gallicagrapher",
            user="wgleason",
            password="ilike2play"
        )
        conn.set_session(autocommit=True)
        self.dbConnection = conn



