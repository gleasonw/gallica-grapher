import React from "react";
import { GraphSeriesForm } from "./components/GraphSeriesForm";
import Head from "next/head";
import { apiURL } from "./components/apiURL";
import { GallicaResponse, GraphData } from "./components/models/dbStructs";
import { Chart } from "./components/Chart";
import GraphContextForm from "./components/GraphContextForm";
import { SearchState, getSearchStateFromURL } from "./utils/searchState";
import { GraphState, getGraphStateFromURL } from "./utils/getGraphStateFromURL";
import { addQueryParamsIfExist } from "./utils/addQueryParamsIfExist";
import { fetchSRU } from "./components/fetchContext";
import { VolumeContext } from "./components/VolumeContext";
import { getSeries } from "./gallicagram";

const strings = {
  fr: {
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
  },
  en: {
    description: "Explore word occurrences in archived Gallica periodicals.",
  },
};

export default async function Page({
  searchParams,
}: {
  searchParams: Record<string, any>;
}) {
  const translation = strings["fr"];

  const searchState = getSearchStateFromURL(searchParams);

  const graphState = getGraphStateFromURL(searchParams);

  let numResults: undefined | number = undefined;
  let seriesData: undefined | GraphData[] = undefined;
  let data: Awaited<ReturnType<typeof fetchSRU>> | undefined = undefined;

  if (searchState) {
    data = await fetchSRU({
      ...searchState,
      terms: searchState.selected_term
        ? [searchState.selected_term]
        : searchState.terms?.slice(0) ?? [],
    });
    numResults = data.total_records;
    const response = await Promise.allSettled(
      searchState.terms?.map(
        async (term) =>
          await getSeries(
            {
              term: term,
              year: searchState.year,
              end_year: searchState.end_year,
              grouping: "mois",
              smoothing: graphState.smoothing,
              source: "presse",
            },
            () => console.log("test")
          )
      ) ?? []
    );
    seriesData = response
      .map((r) => (r.status === "fulfilled" ? r.value : undefined))
      .filter((r) => r !== undefined) as GraphData[];
  }

  function getArkImageFromParams(ark: string) {
    if (Object.keys(searchParams)?.includes(`arkPage${ark}`)) {
      return searchParams[`arkPage${ark}`];
    }
  }

  function getImageStatusFromParams(ark: string) {
    if (Object.keys(searchParams)?.includes(`${ark}-withImage`)) {
      return searchParams[`${ark}-withImage`] === "true";
    }
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
        <GraphContextForm numResults={numResults}>
          <div className={"flex flex-col gap-20 md:m-5"}>
            {data?.records?.map((record, index) => (
              <div
                key={`${record.ark}-${record.terms}-${index}`}
                className={
                  "border-gray-400 border md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5  w-full"
                }
              >
                <h1 className={"flex flex-col gap-5 flex-wrap"}>
                  <span className={"text-lg font-bold"}>
                    {record.paper_title}
                  </span>
                  <span>{record.date}</span>
                  <span>{record.author}</span>
                </h1>
                <VolumeContext
                  ark={record.ark}
                  term={record.terms[0]}
                  pageNum={getArkImageFromParams(record.ark)}
                  showImage={getImageStatusFromParams(record.ark)}
                />
              </div>
            ))}
          </div>
        </GraphContextForm>
      </div>
    </>
  );
}
