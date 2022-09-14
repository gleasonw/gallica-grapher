from date import Date
from occurrenceRecord import OccurrenceRecord
from paperRecord import PaperRecord
from parse import Parse
from xmlParser import XMLParser


def buildParser() -> Parse:
    return Parse(
        makePaperRecord=PaperRecord,
        makeOccurrenceRecord=OccurrenceRecord,
        xmlParser=XMLParser(Date)
    )
