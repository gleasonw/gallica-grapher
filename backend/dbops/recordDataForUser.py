import concurrent.futures

from utils.psqlconn import PSQLconn
from query import OCRQuery
from fetch.fetch import Fetch
from factories.parseFactory import buildParser


class RecordDataForUser:

    ticketResultsWithPaperName = """
    SELECT searchterm, title, year, month, day, identifier
    FROM results
    JOIN papers
    ON results.paperid = papers.code
    WHERE ticketid in %s
    AND requestid = %s
    """

    def __init__(self):
        self.conn = PSQLconn().getConn()
        self.csvData = None
        self.parse = buildParser()

    #TODO: compress csv before returning to user
    def getCSVData(self, ticketIDs, requestID):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            ORDER BY year, month, day
            """, (tupledTickets,requestID))
            self.csvData = cur.fetchall()
        rowLabels = ['ngram', 'identifier', 'periodical', 'year', 'month', 'day']
        self.csvData.insert(0, rowLabels)
        return self.csvData

    def getRecordsForDisplay(self, ticketIDs, requestID, year, month, day, limit, offset):
        if year and month and day:
            records = self.getYearMonthDayRecordsForDisplay(ticketIDs, requestID, year, month, day, limit, offset)
        elif year and month:
            records = self.getYearMonthRecordsForDisplay(ticketIDs, requestID, year, month, limit, offset)
        elif year:
            records = self.getYearRecordsForDisplay(ticketIDs, requestID, year, limit, offset)
        else:
            return []
        arkCodesToRecords = {
            (record[5].split('/').pop()): record
            for record in records
        }
        queries = [
            OCRQuery(ark=ark, term=record[0])
            for ark, record in arkCodesToRecords.items()
        ]
        fetcher = Fetch(
            'https://gallica.bnf.fr/services/ContentSearch',
            maxSize=len(queries)
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(45, len(queries))) as executor:
            for data, ark in executor.map(fetcher.get, queries):
                numResults, pagesWithContents = self.parse.OCRtext(data)
                arkRecord = arkCodesToRecords[ark]
                arkCodesToRecords[ark] = arkRecord + (numResults, pagesWithContents)
        return list(arkCodesToRecords.values())

    def getYearRecordsForDisplay(self, ticketIDs, requestID, year, limit, offset):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            AND year = %s
            ORDER BY year, month, day
            LIMIT %s
            OFFSET %s
            ; 
            """, (tupledTickets, requestID, year, limit, offset))
            return cur.fetchall()

    def getYearMonthRecordsForDisplay(self, ticketIDs, requestID, year, month, limit, offset):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            AND year = %s 
            AND month = %s
            ORDER BY year, month, day
            LIMIT %s
            OFFSET %s
            """, (tupledTickets, requestID, year, month, limit, offset))
            return cur.fetchall()

    def getYearMonthDayRecordsForDisplay(self, ticketIDs, requestID, year, month, day, limit, offset):
        tupledTickets = tuple(ticketIDs.split(','))
        with self.conn.cursor() as cur:
            cur.execute(f"""
            {self.ticketResultsWithPaperName}
            AND year = %s 
            AND month = %s
            AND day = %s
            ORDER BY year, month, day
            LIMIT %s
            OFFSET %s
            """, (tupledTickets, requestID, year, month, day, limit, offset))
            return cur.fetchall()

    def clearUserRecordsAfterCancel(self, requestID):
        with self.conn.cursor() as cur:
            cur.execute("""
            DELETE FROM results
            WHERE requestid = %s
            """, (requestID,))
            self.conn.commit()


