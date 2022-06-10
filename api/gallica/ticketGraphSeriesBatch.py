import datetime
from .ticketGraphSeries import TicketGraphSeries
import ciso8601
from db import DB


#TODO: refactor return to {'key' : options,'key': options}
class TicketGraphSeriesBatch:
    def __init__(self,
                 requestids,
                 averagewindow=0,
                 groupby='day'):

        self.dbConnection = DB().getConn()
        self.dataBatches = []

        if requestids and groupby:
            self.averageWindow = int(averagewindow)
            self.requestIDs = requestids.split(',')
            self.groupBy = groupby
            self.selectGraphSeries()

    def getSeries(self):
        return self.dataBatches

    def selectGraphSeries(self):
        self.dataBatches = list(map(self.selectDataForRequestID, self.requestIDs))
        self.dbConnection.close()

    def selectDataForRequestID(self, requestID):
        series = TicketGraphSeries(
            requestID,
            self.dbConnection,
            self.averageWindow,
            self.groupBy)
        return {requestID: series.getSeries()}

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
            'legend': {
                'dateTimeLabelFormats': {
                    'month': '%b',
                    'year': '%Y'
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
            'legend': {
                'dateTimeLabelFormats': {
                    'month': '%b',
                    'year': '%Y'
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
            'legend': {
                'dateTimeLabelFormats': {
                    'month': '%b',
                    'year': '%Y'
                }
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



