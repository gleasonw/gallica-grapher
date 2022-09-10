NUM_CODES_PER_CQL = 4

class CQLSelectStringForPapers:
    def __init__(self, codes):
        self.codes = codes
        self.cqlSelectStrings = self.generatePaperCQLWithMaxNUM_CODESCodesEach()

    def generatePaperCQLWithMaxNUM_CODESCodesEach(self):
        cql20CodeStrings = []
        for i in range(0, len(self.codes), NUM_CODES_PER_CQL):
            codes = self.codes[i:i + NUM_CODES_PER_CQL]
            formattedCodes = [f"{code}_date" for code in codes]
            CQLpaperSelectString = 'arkPress all "' + '" or arkPress all "'.join(
                formattedCodes) + '"'
            cql20CodeStrings.append(CQLpaperSelectString)
        return cql20CodeStrings

