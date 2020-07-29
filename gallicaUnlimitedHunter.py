from gallicaHunter import GallicaHunter


class GallicaUnlimitedHunter(GallicaHunter):
    def __init__(self, query, isYearRange, recordNumber):
        super().__init__(query, isYearRange, recordNumber)
        self.totalHits = self.establishTotalHits()

    def hunt(self):
        hasMoreRecords = True
        while hasMoreRecords:

            self.progressReporter()

            parameters = {"version": 1.2, "operation": "searchRetrieve", "collapsing": "false", "query": self.query,
                          "startRecord": startRecord, "maximumRecords": 50}
            response = requests.get("https://gallica.bnf.fr/SRU", params=parameters)
            try:
                root = etree.fromstring(response.content)
            except etree.XMLSyntaxError as e:
                print("\n\n ****Gallica spat at you!**** \n")
                continue

            self.hitListCreator(root)

            startRecord = startRecord + 51




