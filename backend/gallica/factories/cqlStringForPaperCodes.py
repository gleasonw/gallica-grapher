NUM_CODES_PER_CQL = 4


class CQLStringForPaperCodes:
    def __init__(self, numCodesPerCQL=NUM_CODES_PER_CQL):
        self.numCodesPerCQL = numCodesPerCQL

    def build(self, codes):
        cqlStrings = []
        for i in range(0, len(codes), self.numCodesPerCQL):
            codeChunks = codes[i:i + self.numCodesPerCQL]
            formattedCodes = [f"{code}_date" for code in codeChunks]
            CQLpaperSelectString = 'arkPress adj "' + '" or arkPress adj "'.join(
                formattedCodes) + '"'
            cqlStrings.append(CQLpaperSelectString)
        return cqlStrings
