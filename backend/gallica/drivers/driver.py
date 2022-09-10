from occurrenceFetchDriver import OccurrenceFetchDriver
from paperFetchDriver import PaperFetchDriver

CHUNK_SIZE = 200


class Driver:

    def getRecordsForOptions(self, driver):
        if isinstance(driver, OccurrenceFetchDriver):
            urls = driver.getUrlsForOptions(driver.options)
            numResultsForUrls = driver.getNumResultsForURLs(urls)
        elif isinstance(driver, PaperFetchDriver):
            allPaperQuery = driver.getAllPaperQuery()
            queryWithResponse = driver.fetchNoTrack([allPaperQuery])
            responseXML = queryWithResponse[0].responseXML
            numPapers = driver.parse.numRecords(responseXML)
            numResultsForUrls = [(driver.allPaperURL, numPapers)]
        else:
            raise TypeError(f'Invalid fetch driver type: {type(driver)}')
        self.fetchAndInsert(numResultsForUrls, driver)

    def fetchAndInsert(self, numResultsForUrls, driver):
        chunkedQueries = self.buildQueries(numResultsForUrls, driver)
        for chunk in chunkedQueries:
            queriesWithResponseXML = driver.fetch(chunk)
            records = yield from (
                driver.parse(query.responseXML) for query in queriesWithResponseXML
            )
            records = driver.prepareRecordsForInsert(records)
            driver.insert(records)

    def buildQueries(self, numResultsForUrls, driver):
        indexedQueries = self.generateIndexedQueries(numResultsForUrls, driver)
        chunkedQueries = self.splitIntoCHUNK_SIZEchunks(indexedQueries)
        return chunkedQueries

    def generateIndexedQueries(self, numResultsForUrls, driver):
        for url, numResults in numResultsForUrls:
            yield self.buildIndex(url, numResults, driver)

    def buildIndex(self, url, numResults, driver):
        for i in range(1, numResults, 50):
            yield driver.makeQuery(
                url=url,
                startIndex=i,
                numRecords=50,
                collapsing=False
            )

    def splitIntoCHUNK_SIZEchunks(self, indexedQueries):
        allChunks = []
        chunk = []
        for query in indexedQueries:
            if len(chunk) < CHUNK_SIZE:
                chunk.append(query)
            else:
                allChunks.append(chunk)
                chunk = [query]
        return allChunks





