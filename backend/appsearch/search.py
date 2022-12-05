from typing import List

import gallicaGetter
from database.recordInsertResolvers import (
    insert_records_into_results
)
from gallicaGetter.gallicaWrapper import (
    VolumeOccurrenceWrapper
)
from gallicaGetter.searchArgs import SearchArgs


def get_and_insert_records_for_args(
        ticketID: str,
        args: SearchArgs,
        onProgressUpdate: callable,
        conn):
    match [args.grouping, bool(args.codes)]:
        case ['all', True] | ['all', False]:
            all_volume_occurrence_search_ticket(
                args=args,
                requestID='test',
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate
            )
        case ['year', False] | ['month', False]:
            pyllica_search_ticket(
                args=args,
                requestID='test',
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate,
            )
        case ['year', True] | ['month', True]:
            period_occurrence_search_ticket(
                args=args,
                requestID='test',
                ticketID=ticketID,
                conn=conn,
                onProgressUpdate=onProgressUpdate
            )
        case _:
            raise ValueError(f'Invalid search type: {args.grouping}, {args.codes}')


def all_volume_occurrence_search_ticket(
        args: SearchArgs,
        conn,
        onProgressUpdate: callable,
        requestID,
        ticketID
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
        insert_hook=insert_records_into_results,
        conn=conn,
        requestID=requestID,
        ticketID=ticketID,
    )


def pyllica_search_ticket(
        args,
        conn,
        requestID,
        ticketID,
        onProgressUpdate):
    pass


def period_occurrence_search_ticket(
        args,
        requestID,
        ticketID,
        conn,
        onProgressUpdate):
    pass


def insert_records_into_db(
        records: List,
        insert_hook: callable,
        conn,
        requestID: str,
        ticketID: str,
        onAddingResults: callable = None,
        onAddingMissingPapers: callable = None):
    return insert_hook(
        records=records,
        conn=conn,
        onAddingResults=onAddingResults,
        onAddingMissingPapers=onAddingMissingPapers,
        requestID=requestID,
        ticketID=ticketID
    )
