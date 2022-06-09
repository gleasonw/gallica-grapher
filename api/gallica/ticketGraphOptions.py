import datetime
import psycopg2
from .ticketGraphSeries import TicketGraphSeries
import ciso8601


class TicketGraphOptions:
    def __init__(self,
                 requestids,
                 averagewindow=0,
                 groupby='day'):

        self.dbConnection = None
        self.dataBatches = []
        self.categories = []
        self.seriesCollection = []
        self.options = {}
        self.lowYear = None
        self.highYear = None
        self.names = []

        self.initDBConnection()
        if requestids and averagewindow and groupby:
            self.averageWindow = int(averagewindow)
            self.requestIDs = requestids.split(',')
            self.groupBy = groupby
            self.selectGraphSeries()

    def getOptions(self):
        return self.options

    def selectGraphSeries(self):
        self.dataBatches = list(map(self.selectDataForRequestID, self.requestIDs))
        self.getBatchNames()
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
        self.parseDatesToJSTimestamp()
        self.formatOptions()

    def parseDatesToJSTimestamp(self):

        def parseBatch(batch):

            def makeMonthTwoDigits(month):
                if month < 10:
                    month = f'0{month}'
                return month

            def makeDayTwoDigits(day):
                if day < 10:
                    day = f'0{day}'
                return day

            def dateToTimestamp(date):
                dateObject = ciso8601.parse_datetime(date)
                timestamp = datetime.datetime.timestamp(dateObject) * 1000
                return timestamp

            #Dummy day added to simplify Highcharts comparison.
            def parseYearMonRecord(record):
                year = record[0]
                month = makeMonthTwoDigits(record[1])
                freq = record[2]
                JStimestamp = dateToTimestamp(f"{year}-{month}-01")
                return [
                    JStimestamp,
                    freq
                ]

            def parseYearMonDayRecord(record):
                year = record[0]
                month = makeMonthTwoDigits(record[1])
                day = makeDayTwoDigits(record[2])
                freq = record[3]
                JStimestamp = dateToTimestamp(f"{year}-{month}-{day}")
                return [
                    JStimestamp,
                    freq
                ]

            if self.groupBy == 'year':
                data = batch["data"]
            elif self.groupBy == 'month':
                data = list(map(
                    parseYearMonRecord,
                    batch["data"]
                ))
            else:
                data = list(map(
                    parseYearMonDayRecord,
                    batch["data"]
                ))
            return {
                'name': batch["keywords"],
                'data': data
            }

        self.seriesCollection = list(map(parseBatch, self.dataBatches))

    def getBatchNames(self):
        self.names = list(map(
            lambda batch: batch["keywords"],
            self.dataBatches
        ))

    def formatOptions(self):
        if self.groupBy == 'year':
            self.formatYearOptions()
        elif self.groupBy == 'month':
            self.formatYearMonOptions()
        else:
            self.formatYearMonDayOptions()

    def formatYearOptions(self):
        self.options = {
            'chart': {
                'zoomType': 'x'
            },
            'plotOptions': {
                'line': {
                    'marker': {
                        'enabled': False
                    }
                }
            },
            'title': {
                'text': None
            },
            'yAxis': {
                'title': {
                    'text': 'Mentions'
                }
            },
            'xAxis': {
                'type': 'line'
            },
            'series': self.seriesCollection
        }

    def formatYearMonOptions(self):
        self.options = {
            'chart': {
                'zoomType': 'X'
            },
            'title': {
                'text': None
            },
            'yAxis': {
                'title': {
                    'text': 'Mentions'
                }
            },
            'xAxis': {
                'type': 'datetime',

                #Don't display the dummy day
                'dateTimeLabelFormats': {
                    'month': '%b',
                    'year': '%Y'
                }
            },
            'series': self.seriesCollection
        }

    def formatYearMonDayOptions(self):
        self.options = {
            'chart': {
                'zoomType': 'X'
            },
            'title': {
                'text': None
            },
            'yAxis': {
                'title': {
                    'text': 'Mentions'
                }
            },
            'xAxis': {
                'type': 'datetime',
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



