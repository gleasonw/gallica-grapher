from utils.psqlconn import PSQLconn
from parseOccurrenceRecords import ParseOccurrenceRecords
from query import OCRQuery
from get import Get
from concurrentFetch import ConcurrentFetch
from gallicaxmlparse import GallicaXMLparse
from query import MomentQuery
from recordGetter import RecordGetter

conn = PSQLconn().getConn()


class RecordDataForUser:

    ticketResultsWithPaperName = """
    SELECT searchterm, papertitle, year, month, day, identifier
    FROM results
    WHERE ticketid in %(tickets)s
    AND requestid = %(requestID)s
    """

    countResultsSelect = """
    SELECT COUNT(*)
    FROM results
    WHERE ticketid in %(tickets)s
    AND requestid = %(requestID)s
    """

    def __init__(self):
        global conn
        self.conn = conn if conn else PSQLconn().getConn()
        self.csvData = None
        self.parse = GallicaXMLparse()

    def getCSVData(self, ticketIDs, requestID):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            """, {'tickets': tupledTickets, 'requestID': requestID})
            self.csvData = cur.fetchall()
        rowLabels = ['ngram', 'identifier', 'periodical', 'year', 'month', 'day']
        self.csvData.insert(0, rowLabels)
        return self.csvData

    def getRecordsForDisplay(self, tableArgs):
        year = tableArgs.get('year')
        month = tableArgs.get('month')
        day = tableArgs.get('day')
        term = tableArgs.get('term')
        periodical = tableArgs.get('periodical')
        if periodical:
            tableArgs['periodical'] = '%' + periodical.lower() + '%'
        tableArgsSelect = f"""
        {'AND year = %(year)s' if year else ''}
        {'AND month = %(month)s' if month else ''}
        {'AND day = %(day)s' if day else ''}
        {'AND searchterm = %(term)s' if term else ''}
        {'AND LOWER(papertitle) LIKE %(periodical)s' if periodical else ''}
        """
        limitOrderingOffset = f"""
        ORDER BY year, month, day
        LIMIT %(limit)s
        OFFSET %(offset)s
        """
        with self.conn.cursor() as cur:

            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            {tableArgsSelect}
            {limitOrderingOffset}
            """, tableArgs)
            records = cur.fetchall()

            cur.execute(f"""
            {self.countResultsSelect}
            {tableArgsSelect}
            """, tableArgs)
            count = cur.fetchone()[0]

        return records, count

    def getOCRTextForRecord(self, ark, term) -> tuple:
        fetcher = Get(
            'https://gallica.bnf.fr/services/ContentSearch',
            maxSize=1
        )
        response = fetcher.get(OCRQuery(ark, term))
        return self.parse.getNumResultsAndPagesForOccurrenceInPeriodical(response.xml)

    def getGallicaRecordsForDisplay(self, ticket, filters):
        records = recordGetter.getFromQueries(
            [
                MomentQuery(
                    term=[filters.get('term')] if filters.get('term') else ticket['terms'],
                    codes=[filters.get('code')] if filters.get('code') else ticket['papersAndCodes'],
                    year=filters.get('year'),
                    month=filters.get('month') or 1,
                    day=filters.get('day') or 1,
                    linkTerm=ticket['linkTerm'],
                    linkDistance=ticket['linkDistance'],
                    startIndex=filters['offset'],
                    numRecords=filters['limit']
                )
            ]
        )
        records = list(records)
        pass

    def clearUserRecordsAfterCancel(self, requestID):
        with self.conn.cursor() as cur:
            cur.execute("""
            DELETE FROM results
            WHERE requestid = %s
            """, (requestID,))
            self.conn.commit()

    def getTopPapers(self, requestID, tickets):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            WITH resultCounts AS (
                SELECT papercode, count(*) as papercount
                FROM results 
                WHERE requestid = %s
                AND ticketid in %s
                GROUP BY papercode
                ORDER BY papercount DESC
                LIMIT 10
            )
            SELECT title, papercount
                FROM resultCounts
                JOIN
                papers
                ON resultCounts.papercode = papers.code;
            """, (requestID, tickets,))
            return cursor.fetchall()

