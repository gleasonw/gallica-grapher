from dateparse import DateParse


class RecordParse:
    @staticmethod
    def getPaperCode(xml) -> str:
        paperCodeElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}relation')

        if paperCodeElement is not None:
            elementText = paperCodeElement.text
            paperCode = elementText[-11:len(elementText)]
            return paperCode

    @staticmethod
    def getURL(xml) -> str:
        urlElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}identifier')
        if urlElement is not None:
            url = urlElement.text
            return url

    @staticmethod
    def getPaperTitle(xml) -> str:
        paperTitle = xml.find(
            '{http://purl.org/dc/elements/1.1/}title').text
        return paperTitle

    @staticmethod
    def getDate(xml) -> DateParse:
        dateElement = xml.find(
            '{http://purl.org/dc/elements/1.1/}date')
        if dateElement is not None:
            return DateParse(dateElement.text)
