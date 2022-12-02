from pyllicagram import pyllicagram as pyllica
from gallicaGetter.parse.date import Date
from gallicaGetter.parse.periodOccurrenceRecord import PeriodOccurrenceRecord


def get(**kwargs):
    convertedArgs = {
        'recherche': kwargs['terms'],
        'somme': True,
        'corpus': 'presse'
    }
    if start := kwargs.get('startDate'):
        convertedArgs['debut'] = Date(start).getYear()
    if end := kwargs.get('endDate'):
        convertedArgs['fin'] = Date(end).getYear()
    if kwargs.get('grouping') == 'year':
        convertedArgs['resolution'] = 'annee'
    return convert_data_frame_to_grouped_record(
        pyllica(**convertedArgs),
        ticketID=kwargs['ticketID'],
        requestID=kwargs['requestID']
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