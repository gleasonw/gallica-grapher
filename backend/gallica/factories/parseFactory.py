from parse import Parse
from search import PaperSearchFulfillment
from search import OccurrenceSearchFulfillment
from paperRecord import PaperRecord
from occurrenceRecord import OccurrenceRecord
from xmlParser import XMLParser
from date import Date


def buildParser() -> Parse:
    return Parse(
        PaperSearchFulfillment,
        OccurrenceSearchFulfillment,
        PaperRecord,
        OccurrenceRecord,
        XMLParser(Date)
    )
