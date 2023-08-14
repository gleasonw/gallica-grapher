import React from "react";
import { GraphSeriesForm } from "./components/InputForm";
import Head from "next/head";
import { apiURL } from "./components/apiURL";
import { GraphData } from "./components/models/dbStructs";
import { Chart } from "./components/Chart";
import GraphContextForm from "./components/GraphContextForm";
import { getSearchStateFromURL } from "./utils/getSearchStateFromURL";
import { GraphState, getGraphStateFromURL } from "./utils/getGraphStateFromURL";
import { SearchPageState } from "./components/SearchStateReducer";
import { addQueryParamsIfExist } from "./utils/addQueryParamsIfExist";
import { fetchSRU } from "./components/fetchContext";

const strings = {
  fr: {
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
  },
  en: {
    description: "Explore word occurrences in archived Gallica periodicals.",
  },
};

async function getPreexistingSeries(args: SearchPageState & GraphState) {
  const ticketSeries = await fetch(
    addQueryParamsIfExist(`${apiURL}/api/graphData`, args)
  );
  return (await ticketSeries.json()) as GraphData;
}

export default async function Page(searchParams: Record<string, any>) {
  const translation = strings["fr"];

  const { searchState, error: searchError } =
    getSearchStateFromURL(searchParams);

  const { graphState, error: graphError } = getGraphStateFromURL(searchParams);

  if (searchError || graphError) {
    console.log(searchError, graphError);
  }

  let numResults: undefined | number = undefined;
  let seriesData: undefined | GraphData = undefined;

  if (searchState) {
    const data = await fetchSRU({
      ...searchState,
      terms: searchState.terms ?? "",
    });
    numResults = data.total_records;
    seriesData = await getPreexistingSeries({
      ...searchState,
      ...graphState,
    });
  }

  return (
    <>
      <Head>
        <title>Gallica Grapher</title>
        <meta
          name="Graph word occurrences in archived French periodicals."
          content="Gallica Grapher"
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={"flex flex-col"}>
        <title>Gallica Grapher</title>
        <div className="m-10 mt-20 text-center text-4xl">
          {" "}
          {translation.description}{" "}
        </div>
        <GraphSeriesForm />
        <Chart series={seriesData} />
        <GraphContextForm numResults={numResults} />
      </div>
    </>
  );
}
