import os.path
import math, datetime
import csv
import rpy2.robjects.lib.ggplot2 as ggplot2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

class GallicaPackager:
    def __init__(self, searchTerm, newspaper, csvEntries, yearRange):
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
        print(self.fileName)
        grdevices = importr('grDevices')
        base = importr('base')
        zoo = importr('zoo')
        utils = importr('utils')
        nameOcc = utils.read_csv(self.fileName)
        datesAsYearMonth = zoo.as_yearmon(nameOcc[0])
        nameOcc[0] = datesAsYearMonth

        grdevices.png(file=self.graphFileName, width=1024, height=768)

        graphOfHits = ggplot2.ggplot(nameOcc) + \
            ggplot2.aes_string(x=nameOcc[0]) + \
            ggplot2.geom_bar(colour='black') + \
            zoo.scale_x_yearmon() + \
            ggplot2.labs(title = self.querySearchTerm + " occurences by year/month", x="Year/month", y="occurence count")
        graphOfHits.plot()

        grdevices.dev_off()

    def makeGraphFileName(self):
        self.graphFileName = self.fileName[0:len(self.fileName)-4]
        self.graphFileName = self.graphFileName + ".png"
