from gallicaGetter.utils.date import Date
from gallicaGetter.periodOccurrenceWrapper import PeriodRecord
from typing import Callable
from urllib.error import HTTPError
import pandas as pd
import urllib


def get(args, on_no_records_found: Callable):
    """Get records from Pyllica. Interpret 500 error as no records found."""
    converted_args = {"recherche": args.terms, "somme": True, "corpus": "presse"}
    if start := args.start_date:
        converted_args["debut"] = Date(start).year
    if end := args.end_date:
        converted_args["fin"] = Date(end).year
    if args.grouping == "year":
        converted_args["resolution"] = "annee"
    try:
        periods = pyllicagram(**converted_args)
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


def pyllicagram(
    recherche, corpus="presse", debut=1789, fin=1950, resolution="default", somme=False
):
    # forked from https://github.com/regicid/pyllicagram
    # credits Benjamin Azoulay and Benoît de Courson

    if not isinstance(recherche, str) and not isinstance(recherche, list):
        raise ValueError("La recherche doit être une chaîne de caractères ou une liste")
    if not isinstance(recherche, list):
        recherche = [recherche]
    assert corpus in [
        "lemonde",
        "livres",
        "presse",
    ], 'Vous devez choisir le corpus parmi "lemonde","livres" et "presse"'
    assert resolution in [
        "default",
        "annee",
        "mois",
    ], 'Vous devez choisir la résolution parmi "default", "annee" ou "mois"'
    for gram in recherche:
        gram = urllib.parse.quote_plus(gram.lower()).replace("-", " ").replace("+", " ")
        gram = gram.replace(" ", "%20")
        df = pd.read_csv(
            f"https://shiny.ens-paris-saclay.fr/guni/corpus={corpus}_{gram}_from={debut}_to={fin}"
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
        if "result" in locals():
            result = pd.concat([result, df])
        else:
            result = df
    if somme:
        result = (
            result.groupby(
                [
                    "annee",
                    *(("mois",) if "mois" in result.columns else ()),
                    *(("jour",) if "jour" in result.columns else ()),
                ]
            )
            .agg({"n": "sum", "total": "mean"})
            .reset_index()
        )
        result["gram"] = "+".join(recherche)
    result["ratio"] = result.n.values / result.total.values
    return result
