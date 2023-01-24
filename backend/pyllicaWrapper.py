from pyllicagram import pyllicagram as pyllica
from gallicaGetter.parse.date import Date
from gallicaGetter.parse.periodRecords import PeriodRecord
from typing import Callable


def get(args, on_no_records_found: Callable):
    converted_args = {"recherche": args.terms, "somme": True, "corpus": "presse"}
    if start := args.start_date:
        converted_args["debut"] = Date(start).getYear()
    if end := args.end_date:
        converted_args["fin"] = Date(end).getYear()
    if args.grouping == "year":
        converted_args["resolution"] = "annee"
    periods = pyllica(**converted_args)
    if all(periods.ratio == 0):
        on_no_records_found()
        return 
    return convert_data_frame_to_grouped_record(periods)


def convert_data_frame_to_grouped_record(frame):
    if "mois" not in frame.columns:
        dates = frame.annee
    else:
        dates = frame.apply(lambda row: f"{row.annee}-{row.mois:02}", axis=1)
    return (
        PeriodRecord(
            date=Date(date),
            count=count,
            term=term,
        )
        for date, count, term in zip(dates, frame.ratio, frame.gram)
    )
