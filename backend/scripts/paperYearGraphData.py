import json
from scripts.psqlconn import PSQLconn


class PaperYearGraphData:

    def __init__(self):
        self.yearOccurrenceArray = None
        self.lowYear = 0
        self.highYear = 0
        self.yearRangeList = None
        self.yearFreqList = []
        self.JSONData = None

    def createChartJSON(self):
        self.getPaperMetadata()
        self.countPublishingPapersInEachYear()
        self.generateYearFrequencyList()
        self.generateJSONfileForGraphing()

    def getPaperMetadata(self):
        conn = PSQLconn().getConn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(startdate) FROM papers WHERE continuous;")
            self.lowYear = cursor.fetchone()[0]
            cursor.execute("SELECT MAX(enddate) FROM papers WHERE continuous;")
            self.highYear = cursor.fetchone()[0]
            self.yearOccurrenceArray = [0 for i in range(self.lowYear, self.highYear + 1)]
            cursor.execute("SELECT startdate, enddate FROM papers WHERE continuous;")
            self.yearRangeList = cursor.fetchall()
        finally:
            if conn is not None:
                conn.close()

    def countPublishingPapersInEachYear(self):
        for yearRange in self.yearRangeList:
            lowerYear = yearRange[0]
            higherYear = yearRange[1]
            if lowerYear and higherYear:
                for i in range(lowerYear, higherYear + 1):
                    indexToIterate = i - self.lowYear
                    self.yearOccurrenceArray[indexToIterate] += 1

    def generateYearFrequencyList(self):
        for i, yearFreq in enumerate(self.yearOccurrenceArray):
            year = i + self.lowYear
            self.yearFreqList.append([year, yearFreq])

    def generateJSONfileForGraphing(self):
        self.JSONData = json.dumps({'data': self.yearFreqList})
        with open('../static/paperJSON.json', 'w') as outFile:
            outFile.write(self.JSONData)

if __name__ == "__main__":
    chartMaker = PaperYearGraphData()
    chartMaker.createChartJSON()
