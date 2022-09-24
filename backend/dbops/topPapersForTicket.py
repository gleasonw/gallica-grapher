from utils.psqlconn import PSQLconn


class TopPapersForTicket:

    def __init__(
            self,
            ticketID,
            requestID,
            continuous,
            dateRange=None):

        self.conn = PSQLconn().getConn()
        self.ticketID = ticketID
        self.requestID = requestID
        self.continuous = continuous.lower() == "true"
        if self.continuous:
            self.lowYear, self.highYear = dateRange.split(",")
        self.topPapers = []

    def getTopPapers(self):
        if self.continuous:
            self.selectTopContinuousPapers()
        else:
            self.selectTopPapers()
        return self.topPapers

    def selectTopPapers(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            WITH ticket AS 
                (SELECT paperid 
                FROM results
                WHERE requestID = %s
                AND ticketid = %s)
            SELECT papers.title, count(paperid) AS papercount
                FROM ticket
                JOIN papers ON ticket.paperid = papers.code 
                GROUP BY papers.title
                ORDER BY papercount DESC
                LIMIT 10;
    
            """, (self.requestID, self.ticketID,))
            self.topPapers = cursor.fetchall()

    def selectTopContinuousPapers(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            WITH ticketPapers AS (
                SELECT paperid
                FROM results
                WHERE ticketid = %s
                AND requestid = %s
            ), paperNames AS (
                SELECT code, title
                FROM papers
                WHERE papers.startdate <= %s AND papers.enddate >= %s
                AND continuous)
            SELECT title, count(paperid) AS papercount
                FROM 
                ticketPapers
                JOIN 
                paperNames
                ON ticketPapers.paperid = paperNames.code 
                GROUP BY title
                ORDER BY papercount DESC
                LIMIT 10;

            """, (self.ticketID, self.requestID, self.lowYear, self.highYear,))
            self.topPapers = cursor.fetchall()
