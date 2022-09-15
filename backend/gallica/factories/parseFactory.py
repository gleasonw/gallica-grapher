from dateparse import DateParse
from occurrenceRecord import OccurrenceRecord
from paperRecord import PaperRecord
from parse import Parse
from recordDataParser import RecordDataParser


def buildParser() -> Parse:
    return Parse(
        makePaperRecord=PaperRecord,
        makeOccurrenceRecord=OccurrenceRecord,
        recordParser=RecordDataParser
    )
