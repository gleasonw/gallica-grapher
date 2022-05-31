from lxml import etree


class Result:

    @staticmethod
    def standardizeSingleDate(dateToStandardize):
        yearMonDay = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        twoYears = re.compile(r"^\d{4}-\d{4}$")
        oneYear = re.compile(r"^\d{4}$")
        oneYearOneMon = re.compile(r"^\d{4}-\d{2}$")
        if not yearMonDay.match(dateToStandardize):
            if oneYear.match(dateToStandardize):
                return dateToStandardize + "-01-01"
            elif oneYearOneMon.match(dateToStandardize):
                return dateToStandardize + "-01"
            elif twoYears.match(dateToStandardize):
                dates = dateToStandardize.split("-")
                lowerDate = int(dates[0])
                higherDate = int(dates[1])
                if higherDate - lowerDate <= 10:
                    newDate = (lowerDate + higherDate) // 2
                    return str(newDate) + "-01-01"
                else:
                    return None
            else:
                return None
        else:
            return dateToStandardize

    def __init__(self, xml):
        self.hitData = xml[0][2]
        self.paper = ''
        self.date = ''
        self.identifier = ''
        self.getDateFromHit()
        self.getPaperFromHit()
        self.getIdentifierFromHit()

    def getPaper(self):
        return self.paper

    def getDate(self):
        return self.date

    def getIdentifier(self):
        return self.identifier

    def getDateFromHit(self):
        dateOfHit = self.hitData.find('{http://purl.org/dc/elements/1.1/}date').text

        self.date = Result.standardizeSingleDate(dateOfHit)

    def getPaperFromHit(self):
        journalOfHit = self.hitData.find('{http://purl.org/dc/elements/1.1/}relation').text
        if journalOfHit:
            self.paper = journalOfHit[-11:len(journalOfHit)]

    def getIdentifierFromHit(self):
        identifierOfHit = data.find('{http://purl.org/dc/elements/1.1/}identifier').text
        self.identifier = identifierOfHit
