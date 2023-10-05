import pandas as pd
from contextlib import asynccontextmanager
from io import StringIO
import os
import aiohttp.client_exceptions
import uvicorn
from typing import List, Literal, Optional, Tuple
from datetime import date as Date
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
import aiohttp

from pydantic import BaseModel


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Series(BaseModel):
    data: List[Tuple[int, float]]
    name: str


@app.get("/series")
async def get(
    term: str,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    grouping: Literal["mois", "annee"] = "mois",
    source: Literal["livres", "presse", "lemonde"] = "presse",
    link_term: Optional[str] = None,
):
    """Get records from Pyllica. Interpret 500 error as no records found."""
    debut = start_date or 1789
    fin = end_date or 1950
    if link_term:
        periods = await get_contain_data(
            mot1=term,
            mot2=link_term,
            corpus=source,
            resolution=grouping,
            debut=debut,
            fin=fin,
        )
    else:
        periods = await get_gram_data(
            gram=term,
            corpus=source,
            resolution=grouping,
            debut=debut,
            fin=fin,
        )
    if all(periods.ratio == 0):
        raise HTTPException(status_code=404, detail="No records found")

    def get_unix_timestamp(row) -> int:
        year = int(row.get("annee", 0))
        month = int(row.get("mois", 0)) - 1 if row.get("mois") else 0

        dt = Date(year, month + 1, 1) if month >= 0 else Date(year, 1, 1)
        return int((dt - Date(1970, 1, 1)).total_seconds())

    data = periods.apply(
        lambda row: (get_unix_timestamp(row), row["ratio"]), axis=1
    ).tolist()

    return Series(
        data=data,
        name=term,
    )


async def get_contain_data(
    mot1: str,
    mot2: str,
    corpus: Literal["lemonde", "livres", "presse"] = "presse",
    debut=1789,
    fin=1950,
    resolution: Literal["default", "annee", "mois"] = "default",
):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://shiny.ens-paris-saclay.fr/guni/contain",
            params={
                "corpus": corpus,
                "mot1": mot1.lower(),
                "mot2": mot2.lower(),
                "from": debut,
                "to": fin,
            },
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=503, detail="Could not connect to Gallicagram! Egads!"
                )
            return await parse_df(
                response=response, resolution=resolution, corpus=corpus
            )


async def get_gram_data(
    gram: str,
    corpus: Literal["lemonde", "livres", "presse"] = "presse",
    debut=1789,
    fin=1950,
    resolution: Literal["default", "annee", "mois"] = "default",
):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://shiny.ens-paris-saclay.fr/guni/query",
            params={
                "corpus": corpus,
                "mot": gram.lower(),
                "from": debut,
                "to": fin,
            },
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=503, detail="Could not connect to Gallicagram! Egads!"
                )
            return await parse_df(
                response=response, resolution=resolution, corpus=corpus
            )


async def parse_df(
    response: aiohttp.ClientResponse,
    resolution: Literal["default", "annee", "mois"] = "default",
    corpus: Literal["lemonde", "livres", "presse"] = "presse",
):
    df = pd.read_csv(StringIO(await response.text()))
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))