import csv
import rpy2.robjects as robjects
import shutil
import os

from rpy2.robjects.lib.ggplot2 import (ggplot, aes,labs,geom_bar)
from rpy2.robjects.packages import importr



class GallicaPackager:
    def __init__(self, newspaper, searchTerm, csvEntries, yearRange, tenMostPapers):
        self.querySearchTerm = searchTerm
        self.querycsvEntries = csvEntries
        self.queryNewspaper = newspaper
        self.queryYearRange = yearRange
        self.fileName = self.determineFileName()
        self.graphFileName = ''
        self.tenMostPapers = tenMostPapers

    def makeCSVFile(self):
        with open(self.fileName, "w", encoding="utf8") as outFile:
            writer = csv.writer(outFile)
            writer.writerow(["date", "journal", "url"])
            #SORT THAT GUY
            for csvEntry in self.querycsvEntries:
                writer.writerow(csvEntry)
        shutil.move(os.path.join("./", self.fileName),os.path.join("./CSVdata", self.fileName))

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
        base = importr('base')
        utils = importr('utils')
        dplyr = importr('dplyr')
        stringr = importr('stringr')
        scales = importr('scales')
        lubridate = importr('lubridate')
        tibble = importr('tibble')

        nameOcc = utils.read_csv(os.path.join("./CSVdata", self.fileName), encoding="UTF-8", stringsAsFactors=False, header=True)
        nameOcc = self.readyColumnsForGraphing(nameOcc)
        print(nameOcc)

        robjects.r('''
        createGraph <- function(dataToGraph, title){
            graphOfHits <- ggplot(dataToGraph, aes(x=yearmon, y=total, fill=fillPaper)) +\
                geom_col() + \
                scale_x_yearmon() + \
                labs(title=title, x="Year/month", y="occurrence count") +\
                theme(axis.text = element_text(size=12), axis.text.x = element_text(angle = 45, hjust = 1))
            plot(graphOfHits)
        }
        ''')
        graphTitle = "{0} paper mentions by year/mon".format(self.querySearchTerm)

        grdevices.png(file=self.graphFileName, width=1920, height=1080)
        dataGrapher = robjects.globalenv['createGraph']
        dataGrapher(nameOcc, graphTitle)
        grdevices.dev_off()
        shutil.move(os.path.join("./", self.graphFileName), os.path.join("./Graphs", self.graphFileName))


    def readyColumnsForGraphing(self, csvResults):
        newspaperVector = robjects.StrVector(self.tenMostPapers)
        robjects.r('''
            nameOccMutateForFill <- function(csvResults, paperVector){ 
                csvResults <- csvResults %>% mutate(date=as.yearmon(date))
                csvResults <- csvResults %>% mutate(fillPaper=ifelse(csvResults$journal %in% paperVector, csvResults$journal, 'Other')) 
                yearMonthCounts <- tibble(yearmon=csvResults$date,fillPaper=csvResults$fillPaper,count=1)\
                                %>% group_by(yearmon, fillPaper)\
                                %>% summarise(total = sum(count))
                return(yearMonthCounts)
                }
            ''')
        mutateFunction = robjects.globalenv['nameOccMutateForFill']
        return mutateFunction(csvResults, newspaperVector)


    def makeGraphFileName(self):
        self.graphFileName = self.fileName[0:len(self.fileName)-4]
        self.graphFileName = self.graphFileName + ".png"
