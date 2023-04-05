from www.models import Ticket
from gallicaGetter.utils.date import Date
from gallicaGetter.periodOccurrence import PeriodRecord
from typing import Callable, Literal
from urllib.error import HTTPError
import pandas as pd
from urllib.parse import quote


def get(args: Ticket, on_no_records_found: Callable):
    """Get records from Pyllica. Interpret 500 error as no records found."""

    if len(args.terms) > 1:
        raise ValueError("Only one term at a time for Pyllica, for now")
    try:
        periods = get_gram_data(
            gram=args.terms[0],
            corpus="presse",
            resolution="mois",
            debut=int(Date(args.start_date).year),
            fin=int(Date(args.end_date).year),
        )
    except HTTPError:
        on_no_records_found()
        return
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
            _date=Date(date),
            count=count,
            term=term,
        )
        for date, count, term in zip(dates, frame.ratio, frame.gram)
    )


def get_gram_data(
    gram: str,
    corpus: Literal["lemonde", "livres", "presse"] = "presse",
    debut=1789,
    fin=1950,
    resolution: Literal["default", "annee", "mois"] = "default",
):
    gram = gram.lower()
    format_gram = quote(gram, encoding="utf-8")
    df = pd.read_csv(
        f"https://shiny.ens-paris-saclay.fr/guni/corpus={corpus}_{format_gram}_from={debut}_to={fin}"
    )
    if resolution == "mois" and corpus != "livres":
        df = (
            df.groupby(["annee", "mois", "gram"])
            .agg({"n": "sum", "total": "sum"})
            .reset_index()
        )
    if resolution == "annee":
        df = (
            df.groupby(["annee", "gram"])
            .agg({"n": "sum", "total": "sum"})
            .reset_index()
        )

    def calc_ratio(row):
        if row.total == 0:
            return 0
        return row.n / row.total

    df["ratio"] = df.apply(lambda row: calc_ratio(row), axis=1)
    return df
