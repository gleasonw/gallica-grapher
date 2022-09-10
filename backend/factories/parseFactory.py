from parse import Parse
from paperFetchDriver import PaperFetchDriver
from occurrenceFetchDriver import OccurrenceFetchDriver
from paperRecord import PaperRecord
from occurrenceRecord import OccurrenceRecord
from xmlParser import XMLParser
from date import Date


def buildParser() -> Parse:
    return Parse(
        PaperFetchDriver,
        OccurrenceFetchDriver,
        PaperRecord,
        OccurrenceRecord,
        XMLParser(Date)
    )
