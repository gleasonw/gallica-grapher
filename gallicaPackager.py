import os.path

class GallicaPackager:
    def __init__(self, searchTerm, newspaper, csvEntries):
        self.searchTerm = searchTerm
        self.csvEntries = csvEntries
        self.newspaper = newspaper

    def makeCSVFile(self):
        fileName = self.determineFileName()
        outFile = open(fileName, "w")
        outFile.write("journal,date,url\n")
        for csvEntry in self.csvEntries:
            outFile.write(csvEntry + "\n")
        outFile.close()

    def determineFileName(self):
        if self.newspaper is None:
            nameOfFile = "AllNewspapers--"
        else:
             nameOfFile = self.newspaper + "--"
             wordsInQuery = self.searchTerm.split(" ")
        for word in wordsInQuery:
            nameOfFile = nameOfFile + word
        nameOfFile = nameOfFile + ".csv"
        return(nameOfFile)
