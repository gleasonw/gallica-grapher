import csv
import rpy2.robjects as robjects
import shutil
import os

from rpy2.robjects.lib.ggplot2 import (ggplot, aes,labs,geom_bar)
from rpy2.robjects.packages import importr



class GallicaGrapher:
    def __init__(self, csvFile, tenMostPapers, graphSettings):
        self.fileName = csvFile
        self.graphFileName = ''
        self.tenMostPapers = []
        self.settings = graphSettings
        self.establishTopPapers(tenMostPapers)
        self.parseGraphSettings()

    def parseGraphSettings(self, settings):
        if self.settings["stackedBar"]:
            self.makeStackedBarGraph()
        elif self.settings["bar"]:
            if self.settings["AllInOne"]:
                self.makeAllInOneBarGraph()
            else:
                self.makeBarGraph()
        elif self.settings["freqPoly"]:
            if self.settings["AllInOne"]:
                self.makeAllInOneFreqPoly()
            else:
                self.makeFreqPoly()
        else:
            pass


    def establishTopPapers(self, tenMostPapers):
        if tenMostPapers is None:
            dictionaryFile = "{0}-{1}".format("TopPaperDict", self.fileName)
            with open(os.path.join("./CSVdata", dictionaryFile)) as inFile:
                reader = csv.reader(inFile)
                for newspaper in reader:
                    thePaper = newspaper[0]
                    self.tenMostPapers.append(thePaper)
        else:
            self.tenMostPapers = tenMostPapers

    def makeStackedBarGraph(self):
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

        robjects.r('''
        createGraph <- function(dataToGraph, title){
            graphOfHits <- ggplot(dataToGraph, aes(x=yearmonth, y=total, fill=fillPaper)) +\
                geom_col() + \
                scale_x_date(date_breaks="years", date_minor_breaks="months", date_labels="%b %Y") + \
                labs(title=title, x="Year/month", y="occurrence count") +\
                theme(axis.text = element_text(size=12), axis.text.x = element_text(angle = 45, hjust = 1))
            plot(graphOfHits)
        }
        ''')
        titleSplit = self.fileName.split("--")
        searchTermProbably = titleSplit[0]
        graphTitle = "{0} usage by year/mon".format(searchTermProbably)

        grdevices.png(file=self.graphFileName, width=1920, height=1080)
        dataGrapher = robjects.globalenv['createGraph']
        dataGrapher(nameOcc, graphTitle)
        grdevices.dev_off()
        shutil.move(os.path.join("./", self.graphFileName), os.path.join("./Graphs", self.graphFileName))

    def makeAllInOneFreqPoly(self):
        pass

    def makeFreqPoly(self):
        pass

    def makeBarGraph(self):
        pass

    def makeAllInOneBarGraph(self):
        pass

    def readyColumnsForGraphing(self, csvResults):
        robjects.r('''
            nameOccMutateForFill <- function(csvResults, topTenPapers){ 
                paperVector <- unlist(topTenPapers,recursive=TRUE)
                csvResults <- csvResults %>% mutate(date=ymd(date), count=1)
                csvResults <- csvResults %>% group_by(yearmonth=floor_date(date, "month"), journal=journal) %>% summarize(total=sum(count))
                csvResults <- csvResults %>% mutate(fillPaper=ifelse(journal %in% paperVector, journal, 'Other')) 
                return(csvResults)
                }
            ''')
        mutateFunction = robjects.globalenv['nameOccMutateForFill']
        return mutateFunction(csvResults, self.tenMostPapers)


    def makeGraphFileName(self):
        self.graphFileName = self.fileName[0:len(self.fileName)-4]
        self.graphFileName = self.graphFileName + ".png"





