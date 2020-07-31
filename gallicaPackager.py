import csv

from rpy2.robjects.lib.ggplot2 import (ggplot, aes_string,labs,geom_bar)
from rpy2.robjects.packages import importr


class GallicaPackager:
    def __init__(self, newspaper, searchTerm, csvEntries, yearRange):
        self.querySearchTerm = searchTerm
        self.querycsvEntries = csvEntries
        self.queryNewspaper = newspaper
        self.queryYearRange = yearRange
        self.fileName = self.determineFileName()
        self.graphFileName = ''

    def makeCSVFile(self):
        with open(self.fileName, "w", encoding="utf8") as outFile:
            writer = csv.writer(outFile)
            writer.writerow(["date", "journal", "url"])
            #SORT THAT GUY
            for csvEntry in self.querycsvEntries:
                writer.writerow(csvEntry)

    def determineFileName(self):
        if self.queryNewspaper == "all":
            nameOfFile = "AllNewspapers--" + self.querySearchTerm + "--"
        else:
            nameOfFile = self.queryNewspaper + "--"
            wordsInQuery = self.querySearchTerm.split(" ")
            for word in wordsInQuery:
                nameOfFile = nameOfFile + word
        if self.queryYearRange:
            lowerYear = self.queryYearRange[0]
            higherYear = self.queryYearRange[1]
            nameOfFile = nameOfFile + " " + str(lowerYear) + "-" + str(higherYear)
        nameOfFile = nameOfFile + ".csv"
        return nameOfFile

    def makeGraph(self):
        self.makeGraphFileName()

        grdevices = importr('grDevices')
        zoo = importr('zoo')
        utils = importr('utils')

        nameOcc = utils.read_csv(self.fileName,encoding="UTF-8", stringsAsFactors=False, header=True)

        datesAsYearMonth = zoo.as_yearmon(nameOcc[0])
        nameOcc[0] = datesAsYearMonth

        grdevices.png(file=self.graphFileName, width=1024, height=768)

        graphOfHits = ggplot(nameOcc) + \
            aes_string(x=nameOcc[0]) + \
            geom_bar(colour='black') + \
            zoo.scale_x_yearmon() + \
            labs(title=self.querySearchTerm + " occurences by year/month", x="Year/month", y="occurence count")
        graphOfHits.plot()

        grdevices.dev_off()

    def makeGraphFileName(self):
        self.graphFileName = self.fileName[0:len(self.fileName)-4]
        self.graphFileName = self.graphFileName + ".png"
