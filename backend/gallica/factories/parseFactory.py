from gallica.dto.occurrenceRecord import OccurrenceRecord
from gallica.dto.paperRecord import PaperRecord
from gallica.parse import Parse
from gallica.recordParse import RecordParse


def buildParser() -> Parse:
    return Parse(
        makePaperRecord=PaperRecord,
        makeOccurrenceRecord=OccurrenceRecord,
        recordParser=RecordParse
    )
