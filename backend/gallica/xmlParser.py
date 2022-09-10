class XMLParser:

    def __init__(self, makeDate):
        self.makeDate = makeDate
        self.xml = None

    def setXML(self, xml):
        self.xml = xml

    def getPaperCode(self):
        paperCodeElement = self.xml.find(
            '{http://purl.org/dc/elements/1.1/}relation')

        if paperCodeElement is not None:
            elementText = paperCodeElement.text
            paperCode = elementText[-11:len(elementText)]
            return paperCode

    def getURL(self):
        urlElement = self.xml.find(
            '{http://purl.org/dc/elements/1.1/}identifier')
        if urlElement is not None:
            url = urlElement.text
            return url

    def getPaperTitle(self):
        paperTitle = self.xml.find(
            '{http://purl.org/dc/elements/1.1/}title').text
        return paperTitle

    def getDate(self, ):
        dateElement = self.xml.find(
            '{http://purl.org/dc/elements/1.1/}date')
        if dateElement is not None:
            return self.makeDate(dateElement.text)

