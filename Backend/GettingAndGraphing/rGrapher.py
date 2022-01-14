import csv
from os.path import dirname

import rpy2.robjects as robjects
import shutil
import os

from rpy2.robjects.packages import importr

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

#REWRITE TO MAKE DATA TRANSFORMATIONS USING SQL, PLOT ONLY IN R
class GallicaGrapher:
    def __init__(self, csvFile, tenMostPapers, graphSettings, requestId, searchTerms):
        self.fileName = csvFile
        self.graphFileName = ''
        self.tenMostPapers = tenMostPapers
        self.searchTerms = searchTerms
        self.papersForTitle = tenMostPapers
        self.settings = graphSettings
        self.theCSVforR = None
        self.ggplotForR = None
        self.breakLength = 360
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.requestId = requestId

    def arrangeGGplotsAndPlot(self, listOfGGplots):
        grdevices = importr('grDevices')
        grdevices.png(file=self.graphFileName, width=1920, height=1080)
        robjects.r('''
        graphMulti <- function(listOfGGplots){
            numberPlots <- length(listOfGGplots)
            nrows <- floor(sqrt(numberPlots))
            do.call("grid.arrange", c(listOfGGplots, nrow=nrows))
        }
        ''')
        multiGraph = robjects.globalenv["graphMulti"]
        multiGraph(listOfGGplots)
        grdevices.dev_off()
        self.moveThatFile()


    def getGGplot(self):
        return self.ggplotForR

    def getFileName(self):
        return self.graphFileName


    def parseGraphSettings(self):
        self.makeGraphFileName()
        self.readCSVtoR()
        if self.settings["graphType"] == "stackedBar":
            self.tenMostPapers = self.transformTopTenPapersToRVector()
            self.makeStackedBarGraph()
        elif self.settings["graphType"] == "bar":
            self.makeBarGraph()
        elif self.settings["graphType"] == "percentBar":
            self.tenMostPapers = self.transformTopTenPapersToRVector()
            self.makePercentBar()
        elif self.settings["graphType"] == "freqPoly":
            self.makeFreqPoly()
        elif self.settings["graphType"] == "multiFreqPoly":
            self.makeMultiFreqPoly()
        elif self.settings["graphType"] == "density":
            self.makeDensityGraph()
        else:
            pass

    def readCSVtoR(self):
        zoo = importr('zoo')
        base = importr('base')
        dplyr = importr('dplyr')
        stringr = importr('stringr')
        scales = importr('scales')
        lubridate = importr('lubridate')
        tibble = importr('tibble')
        grids = importr('gridExtra')
        ggplot2 = importr('ggplot2')
        dtable = importr('data.table')
        self.theCSVforR = dtable.fread(os.path.join("../CSVdata", self.fileName), encoding="UTF-8", header=True, sep=",")
        self.theCSVforR = self.parseDateForRCSV()

    def makeStackedBarGraph(self):
        self.theCSVforR = self.createFillColumnForRCSV()

        robjects.r('''
        initiateStackedBarGGplot <- function(dataToGraph){
            graphOfHits <- ggplot(dataToGraph, aes(x=numericDate, ..count.., fill=Newspaper)) +
                geom_histogram(binwidth=120)
                colors = c("#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080", "#ffffff", "#000000")
                scale_fill_manual(values = colors)
            return(graphOfHits)
        }
        ''')

        ggplotInitiate = robjects.globalenv['initiateStackedBarGGplot']
        self.ggplotForR = ggplotInitiate(self.theCSVforR)
        graphTitle = self.makeSingleGraphTitle()
        self.ggplotForR = self.addLabelsToGGplot(graphTitle)

    def makeDensityGraph(self):
        self.theCSVforR = self.createFillColumnForRCSV()
        robjects.r('''
        initiateDensityGGplot <- function(dataToGraph){
            graphOfHits <- ggplot(dataToGraph, aes(x=numericDate, ..count.., fill=Newspaper)) +
                geom_density(position="stack")
                colors = c("#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080", "#ffffff", "#000000")
                scale_fill_manual(values = colors)
            return(graphOfHits)
        }
        ''')

        ggplotInitiate = robjects.globalenv['initiateDensityGGplot']
        self.ggplotForR = ggplotInitiate(self.theCSVforR)
        graphTitle = self.makeSingleGraphTitle()
        self.ggplotForR = self.addLabelsToGGplot(graphTitle)

    def makeFreqPoly(self):
        robjects.r('''
        initiateFreqPolyGGplot <- function(dataToGraph){
            graphOfHits <- ggplot(dataToGraph, aes(x=numericDate, y=..count..)) +
                geom_freqpoly(binwidth=30)
            return(graphOfHits)
        }
        ''')

        freqPolyInitiate = robjects.globalenv['initiateFreqPolyGGplot']
        self.ggplotForR = freqPolyInitiate(self.theCSVforR)
        graphTitle = self.makeSingleGraphTitle()
        self.ggplotForR = self.addLabelsToGGplot(graphTitle)

    def makeMultiFreqPoly(self):
        robjects.r('''
        initiateManyFreqPolyGGplot <- function(dataToGraph){
            graphOfHits <- ggplot(dataToGraph, aes(x=numericDate, colour=term)) +
                geom_freqpoly(binwidth=30)
            return(graphOfHits)
        }
        ''')

        initiateManyFreqPoly = robjects.globalenv['initiateManyFreqPolyGGplot']

        self.ggplotForR = initiateManyFreqPoly(self.theCSVforR)
        graphTitle = self.graphFileName
        self.ggplotForR = self.addLabelsToGGplot(graphTitle)

    def makeBarGraph(self):

        robjects.r('''
        initiateBarGGplot <- function(dataToGraph){
            graphOfHits <- ggplot(dataToGraph, aes(x=numericDate, ..count..)) +
                geom_histogram(binwidth=30)
            return(graphOfHits)
        }
        ''')

        initiateBar = robjects.globalenv['initiateBarGGplot']
        self.ggplotForR = initiateBar(self.theCSVforR)
        graphTitle = self.makeSingleGraphTitle()
        self.ggplotForR = self.addLabelsToGGplot(graphTitle)

    def makePercentBar(self):
        self.theCSVforR = self.createFillColumnForRCSV()
        robjects.r('''
        initiatePercentGGplot <- function(dataToGraph){
            graphOfHits <- ggplot(dataToGraph, aes(x=numericDate,..count.., fill=Newspaper)) +
                        geom_histogram(binwidth=30, position="fill")
            return(graphOfHits)
        }
        ''')

        initiateBar = robjects.globalenv['initiatePercentGGplot']
        self.ggplotForR = initiateBar(self.theCSVforR)
        graphTitle = self.makeSingleGraphTitle()
        self.ggplotForR = self.addLabelsToGGplot(graphTitle)

    #This feels slow
    def addLabelsToGGplot(self, title):
        #Removed the title for presentation purposes
        robjects.r('''
            labelAdder <- function(theGGplot, title, csvResults, breakLength){
                seqForLabels <- seq(min(csvResults$num)-15,max(csvResults$num),breakLength)
                seqForLabels <- as_date(seqForLabels)
                seqForLabels <- format(seqForLabels, "%b %Y")
                theGGplot <- theGGplot + scale_x_continuous(breaks = seq(min(csvResults$numericDate)-15,max(csvResults$numericDate),breakLength),
                                            minor_breaks = seq(min(csvResults$num)-15,max(csvResults$num),30),
                                            labels = seqForLabels)
                theGGplot <- theGGplot + labs(y="# of word appearances")
                theGGplot <- theGGplot + theme(axis.title = element_text(size=18), axis.text.x = element_text(angle = 45, hjust = 1, size = 14),
                                        axis.text.y = element_text(size = 20), axis.title.x = element_blank())
                theGGplot <- theGGplot + theme(panel.background = element_rect(fill = "white"))
                return(theGGplot)
            }
        ''')
        labelAdder = robjects.globalenv['labelAdder']
        return labelAdder(self.ggplotForR, title, self.theCSVforR, self.breakLength)

    #This feels slow
    def parseDateForRCSV(self):
        robjects.r('''
            parseDate <- function(csvResults){ 
                csvResults <- csvResults %>% mutate(date=ymd(date))
                csvResults <- csvResults %>% mutate(date=floor_date(date, "months"))
                csvResults <- csvResults %>% mutate(numericDate = as.numeric(date))
                return(csvResults)
                }
            ''')
        mutateFunction = robjects.globalenv['parseDate']
        return mutateFunction(self.theCSVforR)

    #This feels slow
    def createFillColumnForRCSV(self):
        robjects.r('''
            createFillColumn <- function(csvResults, paperVector){
                csvResults <- csvResults %>% mutate(Newspaper=ifelse(journal %in% paperVector, journal, 'Other')) 
            }
        ''')
        createFillColumn = robjects.globalenv['createFillColumn']
        return createFillColumn(self.theCSVforR, self.tenMostPapers)

    def transformTopTenPapersToRVector(self):
        robjects.r('''
            ListToVector <- function(listOfPapers){
                paperVector <- unlist(listOfPapers,recursive=TRUE)
                return(paperVector)
            }
        ''')
        vectorTransform = robjects.globalenv['ListToVector']
        return vectorTransform(self.tenMostPapers)

    def plotGraphAndMakePNG(self):
        grdevices = importr('grDevices')
        grdevices.png(file=os.path.join(self.directory, self.graphFileName), width=1920, height=1080)
        robjects.r('''
            graphThatGGplot <- function(theGraph){
                plot(theGraph)
            }
            '''
        )
        dataGrapher = robjects.globalenv['graphThatGGplot']
        dataGrapher(self.ggplotForR)
        grdevices.dev_off()
        self.moveThatFile()

    def moveThatFile(self):
        pathToStaticFolder = dirname(dirname(dirname(os.path.realpath(__file__))))
        pathToStaticFolder = os.path.join(pathToStaticFolder, 'Frontend/static')
        shutil.move(self.graphFileName, os.path.join(pathToStaticFolder, self.graphFileName))

    def makeGraphFileName(self):
        self.graphFileName = self.fileName[0:len(self.fileName)-4]
        self.graphFileName = "{0}-{1}-{2}".format(self.graphFileName, self.settings["graphType"], self.requestId)
        self.graphFileName = self.graphFileName + ".png"



    def makeSingleGraphTitle(self):
        paperNames = ''
        for row in self.papersForTitle:
            paper = row[0]
            paperNames = paperNames + paper + ', '
        paperNames = paperNames[0:len(paperNames)-2]
        graphTitle = "Usage of '{term}' in {papers} by year/mon".format(term = self.searchTerms, papers=paperNames)
        return graphTitle







