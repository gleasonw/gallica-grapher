from lxml import etree


class Record:
    def __init__(self, root):
        record = root[2]
        self.recordData = record[0]
        self.valid = None
        self.paperCode = ''
        self.date = ''
        self.url = ''
        self.parsePaperCodeFromXML()
        self.parseURLFromXML()

    def getPaperCode(self):
        return self.paperCode

    def getDate(self):
        return self.date

    def getUrl(self):
        return self.url

    def isValid(self):
        return self.valid

    def parsePaperCodeFromXML(self):
        paperCode = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}relation').text

        if paperCode:
            self.paperCode = paperCode[-11:len(paperCode)]

    def parseURLFromXML(self):
        self.url = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}identifier').text

    def checkIfValid(self):
        pass


class KeywordRecord(Record):

    def __init__(self, root):
        super().__init__(root)
        self.parseDateFromXML()
        self.checkIfValid()

    def parseDateFromXML(self):
        dateElement = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}date')
        if dateElement is not None:
            self.date = dateElement.text

    def checkIfValid(self):
        if self.date and self.paperCode:
            self.valid = True
        else:
            self.valid = False


class PaperRecord(Record):

    def __init__(self, root, gallicaSession):
        super().__init__(root)
        self.title = ''
        self.publishingYears = []
        self.continuousRange = None
        self.session = gallicaSession
        self.checkIfValid()
        self.parseTitleFromXML()
        self.fetchYearsPublished()
        self.parseYears()
        self.checkIfYearsContinuous()
        self.generateAvailableRange()

    def getTitle(self):
        return self.title

    def getContinuous(self):
        return self.continuousRange

    #TODO: Could this be really slow?
    def fetchYearsPublished(self):
        paramsForArk = {'ark': f'ark:/12148/{self.paperCode}/date'}
        response = self.session.get("",
                                    params=paramsForArk,
                                    timeout=15)
        try:
            root = etree.fromstring(response.content)
            for yearElement in root.iter("year"):
                if yearElement is not None:
                    year = yearElement.text
                    if year.isdigit():
                        self.publishingYears.append(int(year))
        except etree.XMLSyntaxError:
            pass

    def parseYears(self):
        if self.publishingYears:
            self.checkIfYearsContinuous()
            self.generateAvailableRange()
        else:
            self.date = [None, None]

    def checkIfYearsContinuous(self):
        for i, year in enumerate(self.publishingYears):
            if i == len(self.publishingYears) - 1:
                self.continuousRange = True
                return
            nextYear = self.publishingYears[i + 1]
            if year + 1 != nextYear:
                self.continuousRange = False
                return

    def generateAvailableRange(self):
        if self.publishingYears:
            lowYear = self.publishingYears[0]
            highYear = self.publishingYears[-1]
            self.date = [lowYear, highYear]

    def parseTitleFromXML(self):
        self.title = self.recordData.find(
            '{http://purl.org/dc/elements/1.1/}title').text

    def checkIfValid(self):
        if self.paperCode:
            self.valid = True
        else:
            self.valid = False
