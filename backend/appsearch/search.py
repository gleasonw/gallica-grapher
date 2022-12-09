from typing import List
import appsearch.pyllicaWrapper as pyllicaWrapper
import gallicaGetter
from database.recordInsertResolvers import (
    insert_records_into_results,
    insert_records_into_groupcounts
)
from gallicaGetter.gallicaWrapper import (
    VolumeOccurrenceWrapper,
    PeriodOccurrenceWrapper
)
from gallicaGetter.searchArgs import SearchArgs


def get_and_insert_records_for_args(
        ticketID: str,
        requestID: str,
        args: SearchArgs,
        onProgressUpdate: callable,
        conn,
        api=None
):
    match [args.grouping, bool(args.codes)]:
        case ['all', True] | ['all', False]:
            all_volume_occurrence_search_ticket(
                args=args,
                requestID=requestID,
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate,
                api=api
            )
        case ['year', False] | ['month', False]:
            pyllica_search_ticket(
                args=args,
                requestID=requestID,
                ticketID=ticketID,
                conn=conn
            )
        case ['year', True] | ['month', True]:
            period_occurrence_search_ticket(
                args=args,
                requestID=requestID,
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate,
                api=api
            )
        case _:
            raise ValueError(f'Invalid search type: {args.grouping}, {args.codes}')


def all_volume_occurrence_search_ticket(
        args: SearchArgs,
        conn,
        onProgressUpdate: callable,
        requestID: str,
        ticketID: str,
        api=None
):
    api: VolumeOccurrenceWrapper = gallicaGetter.connect('volume')
    records = api.get(
        terms=args.terms,
        start_date=args.start_date,
        end_date=args.end_date,
        codes=args.codes,
        link_term=args.link_term,
        link_distance=args.link_distance,
        onProgressUpdate=onProgressUpdate,
        query_cache=args.query_cache,
        generate=True,
        num_workers=50
    )
    insert_records_into_db(
        records=records,
        insert_into_results=True,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
    )


def pyllica_search_ticket(
        args: SearchArgs,
        conn,
        requestID: str,
        ticketID: str):
    records = pyllicaWrapper.get(args)
    insert_records_into_db(
        records=records,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
    )


def period_occurrence_search_ticket(
        args: SearchArgs,
        requestID: str,
        ticketID: str,
        conn,
        onProgressUpdate: callable,
        api=None
):
    api: PeriodOccurrenceWrapper = gallicaGetter.connect('period')
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
        requestID: str,
        ticketID: str,
        insert_into_results: bool = False,
        onAddingMissingPapers: callable = None
):
    if insert_into_results:
        insert_records_into_results(
            records=records,
            conn=conn,
            requestID=requestID,
            ticketID=ticketID,
            onAddingMissingPapers=onAddingMissingPapers
        )
    else:
        insert_records_into_groupcounts(
            records=records,
            conn=conn,
            requestID=requestID,
            ticketID=ticketID
        )
