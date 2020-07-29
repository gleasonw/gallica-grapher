from gallicaHunter import GallicaHunter


class GallicaLimitedHunter(GallicaHunter):
    def __init__(self, query, isYearRange, recordNumber):
        super().__init__(query, isYearRange, recordNumber)
