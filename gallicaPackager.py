import os.path
import math, datetime
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
        outFile = open(self.fileName, "w")
        outFile.write("journal,date,url\n")
        for csvEntry in self.querycsvEntries:
            outFile.write(csvEntry + "\n")
        outFile.close()

    def determineFileName(self):
        if (self.queryNewspaper is None) or (self.queryNewspaper == "all"):
            nameOfFile = "AllNewspapers--"
        else:
             nameOfFile = self.queryNewspaper + "--"
             wordsInQuery = self.querySearchTerm.split(" ")

        for word in wordsInQuery:
            nameOfFile = nameOfFile + word

        if len(self.queryYearRange) != 0:
            lowerYear = self.queryYearRange[0]
            higherYear = self.queryYearRange[1]
            nameOfFile = nameOfFile + " " + lowerYear + "-" + higherYear
        nameOfFile = nameOfFile + ".csv"
        return(nameOfFile)

    def makeGraph(self):
        self.makeGraphFileName()

        grdevices = importr('grDevices')
        base = importr('base')
        zoo = importr('zoo')
        utils = importr('utils')

        nameOcc = robjects.DataFrame.from_csvfile(self.fileName)
        datesAsYearMonth = zoo.as_yearmon(nameOcc[0])
        nameOcc[0] = datesAsYearMonth

        grdevices.png(file=self.graphFileName, width=1024, height=768)

        graphOfHits = ggplot2.ggplot(nameOcc) + \
            ggplot2.aes_string(x=nameOcc[0]) + \
            ggplot2.geom_bar(colour='black') + \
            zoo.scale_x_yearmon() + \
            ggplot2.ylab(self.searchTerm) + \
            ggplot2.xlab("Year/month")
        graphOfHits.plot()

        grdevices.dev_off()

    def makeGraphFileName(self):
        self.graphFileName = self.fileName[0:len(self.fileName)-4]
        self.graphFileName = self.graphFileName + ".png"
