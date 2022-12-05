from pyllicagram import pyllicagram as pyllica
from gallicaGetter.parse.date import Date
from gallicaGetter.parse.periodOccurrenceRecord import PeriodOccurrenceRecord
from gallicaGetter.searchArgs import SearchArgs


def get(
        args: SearchArgs
):
    convertedArgs = {
        'recherche': args.terms,
        'somme': True,
        'corpus': 'presse'
    }
    if start := args.start_date:
        convertedArgs['debut'] = Date(start).getYear()
    if end := args.end_date:
        convertedArgs['fin'] = Date(end).getYear()
    if args.grouping == 'year':
        convertedArgs['resolution'] = 'annee'
    return convert_data_frame_to_grouped_record(
        pyllica(**convertedArgs),
        ticketID=args.ticketID,
        requestID=args.requestID
    )


def convert_data_frame_to_grouped_record(df, ticketID, requestID):
    if 'mois' not in df.columns:
        dates = df.annee
    else:
        dates = df.apply(
            lambda row: f'{row.annee}-{row.mois:02}',
            axis=1
        )
    return (
        PeriodOccurrenceRecord(
            date=Date(date),
            count=count,
            ticketID=ticketID,
            term=term,
            requestID=requestID
        )
        for date, count, term in zip(dates, df.ratio, df.gram)
    )