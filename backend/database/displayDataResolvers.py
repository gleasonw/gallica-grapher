import gallicaGetter


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


def get_csv_data_for_request(ticketIDs, requestID, conn):
    tupledTickets = tuple(ticketIDs.split(','))
    with conn.cursor() as cur:
        cur.execute(f"""
        {ticketResultsWithPaperName}
        """, {'tickets': tupledTickets, 'requestID': requestID})
        csvData = cur.fetchall()
    rowLabels = ['ngram', 'identifier', 'periodical', 'year', 'month', 'day']
    csvData.insert(0, rowLabels)
    return csvData


def get_display_records(tableArgs, conn):
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
    with conn.cursor() as cur:

        cur.execute(f"""
        {ticketResultsWithPaperName}
        {tableArgsSelect}
        {limitOrderingOffset}
        """, tableArgs)
        records = cur.fetchall()

        cur.execute(f"""
        {countResultsSelect}
        {tableArgsSelect}
        """, tableArgs)
        count = cur.fetchone()[0]

    return records, count


def get_ocr_text_for_record(ark, term) -> tuple:
    wrapper = gallicaGetter.connect('content')
    return wrapper.get(ark, term)[0]


def get_gallica_records_for_display(tickets, filters):
    wrapper = gallicaGetter.connect('sru')
    records = []
    for ticket in tickets:
        argsBundle = {
            **ticket,
            'numRecords': filters.get('limit'),
            'startRecord': filters.get('offset'),
        }
        records.extend(wrapper.get(**argsBundle))
    records.sort(key=lambda record: record.date.getDate())
    return records


def clear_records_for_requestid(requestID, conn):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM results
        WHERE requestid = %s
        """, (requestID,))


def get_top_papers_for_tickets(requestID, tickets, conn):
    with conn.cursor() as cursor:
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

