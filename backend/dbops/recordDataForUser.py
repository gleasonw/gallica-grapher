from gallica.gallicaxmlparse import GallicaXMLparse
import gallica.gallicaWrapper as gallicaWrapper
from dbops.connContext import getConn

conn = getConn()


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
        self.csvData = None
        self.parse = GallicaXMLparse()

    def getCSVData(self, ticketIDs, requestID):
        tupledTickets = tuple(ticketIDs.split(','))
        dbConn = getConn()
        with dbConn.cursor() as cur:
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
        dbConn = getConn()
        with dbConn.cursor() as cur:

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
        wrapper = gallicaWrapper.connect('content')
        return wrapper.get(ark, term)[0]

    def getGallicaRecordsForDisplay(self, tickets, filters):
        wrapper = gallicaWrapper.connect('sru')
        records = []
        for ticket in tickets:
            argsBundle = {
                **ticket,
                'numRecords': filters.get('limit'),
                'startRecord': filters.get('offset'),
            }
            records.extend(wrapper.get(**argsBundle))
        return records

    def clearUserRecordsAfterCancel(self, requestID):
        dbConn = getConn()
        with dbConn.cursor() as cur:
            cur.execute("""
            DELETE FROM results
            WHERE requestid = %s
            """, (requestID,))

    def getTopPapers(self, requestID, tickets):
        dbConn = getConn()
        with dbConn.cursor() as cursor:
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

