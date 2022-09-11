from parse import Parse
from searchlauncher import PaperSearchFulfillment
from searchlauncher import OccurrenceSearchFulfillment
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
