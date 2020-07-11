import os.path

class GallicaPackager:
    def __init__(self, searchTerm, newspaper, csvEntries, yearRange):
        self.querySearchTerm = searchTerm
        self.querycsvEntries = csvEntries
        self.queryNewspaper = newspaper
        self.queryYearRange = yearRange

    def makeCSVFile(self):
        fileName = self.determineFileName()
        outFile = open(fileName, "w")
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
