from typing import List
import pyllicaWrapper as pyllicaWrapper
import gallicaGetter
from database.recordInsertResolvers import (
    insert_records_into_results,
    insert_records_into_groupcounts,
)
from gallicaGetter.gallicaWrapper import (
    VolumeOccurrenceWrapper,
    PeriodOccurrenceWrapper,
)
from main import Ticket
from ticketWithCachedResponse import TicketWithCachedResponse


def get_and_insert_records_for_args(
    ticketID: int,
    requestID: int,
    args: Ticket,
    onProgressUpdate: callable,
    conn,
    api=None,
    onAddingMissingPapers: callable = None,
):
    match [args.grouping, bool(args.codes)]:
        case ["all", True] | ["all", False]:
            all_volume_occurrence_search_ticket(
                ticket=args,
                requestID=requestID,
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate,
                onAddingMissingPapers=onAddingMissingPapers,
                api=api,
            )
        case ["year", False] | ["month", False]:
            pyllica_search_ticket(
                args=args, requestID=requestID, ticketID=ticketID, conn=conn
            )
        case ["year", True] | ["month", True]:
            period_occurrence_search_ticket(
                args=args,
                requestID=requestID,
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate,
                api=api,
            )
        case _:
            raise ValueError(f"Invalid search type: {args.grouping}, {args.codes}")


def all_volume_occurrence_search_ticket(
    ticket: Ticket | TicketWithCachedResponse,
    conn,
    onProgressUpdate: callable,
    onAddingMissingPapers: callable,
    requestID: int,
    ticketID: int,
    api=None,
):
    api: VolumeOccurrenceWrapper = gallicaGetter.connect("volume", api=api)
    records = api.get(
        terms=ticket.terms,
        start_date=ticket.start_date,
        end_date=ticket.end_date,
        codes=ticket.codes,
        link_term=ticket.link_term,
        link_distance=ticket.link_distance,
        onProgressUpdate=onProgressUpdate,
        query_cache=type(ticket) == TicketWithCachedResponse and ticket.cached_response,
        generate=True,
        num_workers=50,
    )
    insert_records_into_db(
        records=records,
        insert_into_results=True,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
        onAddingMissingPapers=onAddingMissingPapers,
    )


def pyllica_search_ticket(args: Ticket, conn, requestID: int, ticketID: int):
    records = pyllicaWrapper.get(args)
    insert_records_into_db(
        records=records,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
    )


def period_occurrence_search_ticket(
    args: Ticket,
    requestID: int,
    ticketID: int,
    conn,
    onProgressUpdate: callable,
    api=None,
):
    api: PeriodOccurrenceWrapper = gallicaGetter.connect("period", api=api)
    records = api.get(
        terms=args.terms,
        codes=args.codes,
        start_date=args.start_date,
        end_date=args.end_date,
        onProgressUpdate=onProgressUpdate,
        num_workers=50,
        grouping=args.grouping,
    )
    insert_records_into_db(
        records=records,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
    )


def insert_records_into_db(
    records: List,
    conn,
    requestID: int,
    ticketID: int,
    insert_into_results: bool = False,
    onAddingMissingPapers: callable = None,
):
    if insert_into_results:
        insert_records_into_results(
            records=records,
            conn=conn,
            requestID=requestID,
            ticketID=ticketID,
            onAddingMissingPapers=onAddingMissingPapers,
        )
    else:
        insert_records_into_groupcounts(
            records=records, conn=conn, requestID=requestID, ticketID=ticketID
        )
