from typing import List, Optional, Tuple

import gallicaGetter
from gallicaGetter.gallicaWrapper import VolumeOccurrenceWrapper

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


def select_csv_data_for_tickets(ticket_ids: int | List[int], request_id: int, conn):
    tupled_ids = tuple(ticket_ids) if isinstance(ticket_ids, list) else (ticket_ids,)
    with conn.cursor() as cur:
        cur.execute(f"""
        {ticketResultsWithPaperName}
        """, {'tickets': tupled_ids, 'requestID': request_id})
        data = cur.fetchall()
    row_labels = ['ngram', 'identifier', 'periodical', 'year', 'month', 'day']
    data.insert(0, row_labels)
    return data


def select_display_records(
        ticket_ids: List[int],
        request_id: int,
        conn,
        term: Optional[str] = None,
        periodical: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
) -> Tuple[List, int]:
    args = [tuple(ticket_ids) if isinstance(ticket_ids, list) else (ticket_ids,), request_id]
    if periodical:
        periodical = '%' + periodical.lower() + '%'
        args.append(periodical)
    if term:
        term = '%' + term.lower() + '%'
        args.append(term)
    year and args.append(year)
    month and args.append(month)
    day and args.append(day)
    args.append(limit)
    args.append(offset)
    args = tuple(args)
    selects = f"""
    {'AND year = %(year)s' if year else ''}
    {'AND month = %(month)s' if month else ''}
    {'AND day = %(day)s' if day else ''}
    {'AND searchterm = %(term)s' if term else ''}
    {'AND LOWER(papertitle) LIKE %(periodical)s' if periodical else ''}
    """
    limit_ordering_offset = f"""
    ORDER BY year, month, day
    LIMIT %(limit)s
    OFFSET %(offset)s
    """
    with conn.cursor() as cur:
        cur.execute(f"""
        {ticketResultsWithPaperName}
        {selects}
        {limit_ordering_offset}
        """, args)
        records = cur.fetchall()

        cur.execute(f"""
        {countResultsSelect}
        {selects}
        """, args)
        total = cur.fetchone()[0]

    return records, total


def get_ocr_text_for_record(ark_code: int, term: str):
    wrapper = gallicaGetter.connect('content')
    if ' ' in term:
        term = '"' + term + '"'
    return wrapper.get(ark_code, term)[0]


def get_gallica_records_for_display(
        terms: List[str],
        start_date: int,
        link_term: Optional[str],
        link_distance: Optional[int],
        codes: List[str] = None,
        limit: int = None,
        offset: int = None,
):
    wrapper: VolumeOccurrenceWrapper = gallicaGetter.connect('volume')
    records = []
    records.extend(wrapper.get(
        terms=terms,
        start_date=start_date,
        codes=codes,
        link_term=link_term,
        link_distance=link_distance,
        num_results=limit,
        start_index=offset,
    ))
    records.sort(key=lambda record: record.date.getDate())
    return records


def clear_records_for_requestid(requestID, conn):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM results
        WHERE requestid = %s
        """, (requestID,))


def select_top_papers_for_tickets(
        tickets: int | List[int],
        request_id: int,
        conn,
        num_results: int = 10,
):
    if type(tickets) is int:
        tickets = [tickets]
    with conn.cursor() as cursor:
        cursor.execute("""
        WITH resultCounts AS (
            SELECT papercode, count(*) as papercount
            FROM results 
            WHERE requestid = %s
            AND ticketid in %s
            GROUP BY papercode
            ORDER BY papercount DESC
            LIMIT %s
        )
        SELECT title, papercount
            FROM resultCounts
            JOIN
            papers
            ON resultCounts.papercode = papers.code;
        """, (request_id, tickets, num_results))
        return cursor.fetchall()
