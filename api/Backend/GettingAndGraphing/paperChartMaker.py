import psycopg2
import json
#TODO: Cache.
class PaperChartMaker:

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
        for i, yearFreq in enumerate(self.yearOccurrenceArray):
            year = i + 1499
            self.yearFreqList.append([year, yearFreq])
        self.JSONData = json.dumps({'data' : self.yearFreqList})
        with open('../../static/paperJSON.json', 'w') as outFile:
            outFile.write(self.JSONData)

    def getPaperMetadata(self):
        conn = None
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="gallicagrapher",
                user="wgleason",
                password="ilike2play"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(startyear) FROM papers;")
            self.lowYear = cursor.fetchone()[0].year
            cursor.execute("SELECT MAX(endyear) FROM papers;")
            self.highYear = cursor.fetchone()[0].year
            self.yearOccurrenceArray = [0 for i in range(self.lowYear, self.highYear + 1)]
            cursor.execute("SELECT startyear, endyear FROM papers;")
            self.yearRangeList = cursor.fetchall()
        finally:
            if conn is not None:
                conn.close()

    def countPublishingPapersInEachYear(self):
        for yearRange in self.yearRangeList:
            if yearRange[0] and yearRange[1]:
                lowerYear = yearRange[0].year
                higherYear = yearRange[1].year
                for i in range(lowerYear, higherYear + 1):
                    indexToIterate = i - self.lowYear
                    self.yearOccurrenceArray[indexToIterate] += 1
            elif yearRange[0] and not yearRange[1]:
                lowerYear = yearRange[0].year
                indexToIterate = lowerYear - self.lowYear
                self.yearOccurrenceArray[indexToIterate] += 1
            else:
                pass

if __name__ == "__main__":
    chartMaker = PaperChartMaker()
    chartMaker.createChartJSON()
