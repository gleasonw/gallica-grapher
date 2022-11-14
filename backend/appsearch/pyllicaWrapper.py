from pyllicagram import pyllicagram as pyllica
from gallicaGetter.parse.date import Date
from gallicaGetter.parse.groupedCountRecord import GroupedCountRecord


def get(**kwargs):
    convertedArgs = {
        'recherche': kwargs['terms'],
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
        kwargs['ticketID'],
        kwargs['requestID']
    )


def convert_data_frame_to_grouped_record(df, ticketID, requestID):
    rows = list(zip(df.date, df.ratio, df.gram))
    for row in rows:
        yield GroupedCountRecord(
            date=Date(row[0]),
            count=row[1],
            ticketID=ticketID,
            term=row[2],
            requestID=requestID
        )
