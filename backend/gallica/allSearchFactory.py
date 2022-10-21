from queryIndexer import QueryIndexer
from query import OccurrenceQuery
from gallica.getandput import GetAndPut
from recordGetter import RecordGetter
from parseOccurrenceRecords import ParseOccurrenceRecords


class SearchFactory:

    def build(self, config):
        return self.prepare(config)

    def prepare(self, config):
        return GetAndPut(
            gallicaAPI=config[0],
            insertRecordsIntoDatabase=config[1],
            requestStateHandlers=config[2],
            identifier=config[3]
        )


