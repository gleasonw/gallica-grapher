from gallica.getandput import GetAndPut

def build(argBundles):
    searches = [AllSearch, GroupSearch, PaperSearch]

class Search:

    def __init__(self):
        pass

class GroupedSearch(Search):

    def prepare(self, request):
        queries = self.buildQueriesForTicket(self.ticket)
        return GetAndPut(
            queries=queries,
            insertRecordsIntoDatabase=self.insertIntoGroupCounts,
            recordGetter=RecordGetter(
                gallicaAPI=self.sruFetcher,
                parseData=self.parser,
                onUpdateProgress=self.onUpdateProgress
            ),
            requestStateHandlers={
                'onAddingResultsToDB': self.onAddingResultsToDB
            },
            numRecordsToFetch=len(queries),
            ticketID=self.ticket.getID()
        )

class AllSearch(Search):

    pass

class PaperSearch(Search):

    pass



