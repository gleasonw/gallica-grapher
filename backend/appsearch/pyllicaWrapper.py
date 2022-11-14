from pyllicagram import pyllicagram as pyllica
from gallicaGetter.parse.date import Date
from gallicaGetter.parse.groupedCountRecord import GroupedCountRecord


def get(**kwargs):
    convertedArgs = {
        'recherche': kwargs['terms'],
        'corpus': 'presse',
        'somme': True
    }
    if start := kwargs.get('startDate'):
        convertedArgs['debut'] = Date(start).getYear()
    if end := kwargs.get('endDate'):
        convertedArgs['fin'] = Date(end).getYear()
    if kwargs.get('grouping') == 'year':
        convertedArgs['resolution'] = 'annee'
    return convert_data_frame_to_grouped_record(pyllica(**convertedArgs))


def convert_data_frame_to_grouped_record(df):
    if 'mois' not in df.columns:
        dates = df.annee
    else:
        dates = df.apply(
            lambda row: f'{row.annee}-{row.mois:02}',
            axis=1
        )
    return (
        GroupedCountRecord(
            date=Date(date),
            count=count,
            ticketID=0,
            term=term,
            requestID=0
        )
        for date, count, term in zip(dates, df.ratio, df.gram)
    )
