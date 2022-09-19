from gallica.dto.occurrenceRecord import OccurrenceRecord
from gallica.dto.paperRecord import PaperRecord
from gallica.parse import Parse


def buildParser() -> Parse:
    return Parse(
        makePaperRecord=PaperRecord,
        makeOccurrenceRecord=OccurrenceRecord,
    )
