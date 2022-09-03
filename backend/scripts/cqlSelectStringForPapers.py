

class CQLSelectStringForPapers:
    def __init__(self, codes):
        self.codes = codes
        self.cqlSelectStrings = self.generatePaperCQLWithMax20CodesEach()

    def generatePaperCQLWithMax20CodesEach(self):
        cql20CodeStrings = []
        for i in range(0, len(self.codes), 20):
            codes = self.codes[i:i + 20]
            formattedCodes = [f"{code}_date" for code in codes]
            CQLpaperSelectString = 'arkPress all "' + '" or arkPress all "'.join(
                formattedCodes) + '"'
            cql20CodeStrings.append(CQLpaperSelectString)
        return cql20CodeStrings
