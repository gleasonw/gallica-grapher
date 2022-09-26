from utils.psqlconn import PSQLconn


class TopPapersForTicket:

    def __init__(
            self,
            tickets,
            requestID
    ):

        self.conn = PSQLconn().getConn()
        self.tickets = tickets
        self.requestID = requestID
        self.topPapers = []

    def getTopPapers(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
            WITH ticket AS 
                (SELECT paperid 
                FROM results
                WHERE requestID = %s
                AND ticketid in %s)
            SELECT papers.title, count(paperid) AS papercount
                FROM ticket
                JOIN papers ON ticket.paperid = papers.code 
                GROUP BY papers.title
                ORDER BY papercount DESC
                LIMIT 10;
    
            """, (self.requestID, self.tickets,))
            return cursor.fetchall()
