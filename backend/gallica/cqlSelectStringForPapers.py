NUM_CODES_PER_CQL = 4


class CQLSelectStringForPapers:
    def __init__(self, codes, numCodesPerCQL=NUM_CODES_PER_CQL):
        self.numCodesPerCQL = numCodesPerCQL
        self.codes = codes
        self.cqlSelectStrings = self.generatePaperCQLWithMaxNUM_CODESCodesEach()

    def generatePaperCQLWithMaxNUM_CODESCodesEach(self):
        cql20CodeStrings = []
        for i in range(0, len(self.codes), self.numCodesPerCQL):
            codes = self.codes[i:i + self.numCodesPerCQL]
            formattedCodes = [f"{code}_date" for code in codes]
            CQLpaperSelectString = 'arkPress all "' + '" or arkPress all "'.join(
                formattedCodes) + '"'
            cql20CodeStrings.append(CQLpaperSelectString)
        return cql20CodeStrings

