import React from "react";
import { GraphSeriesForm } from "./components/GraphSeriesForm";
import Head from "next/head";
import { Chart } from "./components/Chart";
import GraphContextForm from "./components/GraphContextForm";
import { SearchState, getSearchStateFromURL } from "./utils/searchState";
import { GraphState, getGraphStateFromURL } from "./utils/getGraphStateFromURL";
import { fetchSRU } from "./components/fetchContext";
import { VolumeContext } from "./components/VolumeContext";
import { LoadingProvider } from "./components/LoadingProvider";
import { DataFrame, toJSON } from "danfojs-node";
import * as Papa from "papaparse";
import { GraphData } from "./components/models/dbStructs";
import { addQueryParamsIfExist } from "./utils/addQueryParamsIfExist";
import { NearbyTerms } from "./components/NearbyTerms";

const strings = {
  fr: {
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
  },
  en: {
    description: "Explore word occurrences in archived Gallica periodicals.",
  },
};

type CorpusType = "lemonde" | "livres" | "presse";
type ResolutionType = "default" | "annee" | "mois";

type Ticket = {
  term: string;
  year?: number;
  end_year?: number;
  codes?: string[];
  source: SearchState["source"];
  grouping?: GraphState["grouping"];
  smoothing?: number;
};

type GallicaGramRow = {
  n_sum: number;
  gram: string;
  annee: string;
  mois: string;
  total_sum: number;
  ratio: number;
};

async function getSeries(
  { term, year, end_year, grouping, source }: Ticket,
  onNoRecordsFound: (error: any) => void
): Promise<GraphData | undefined> {
  if (!term) {
    return;
  }
  const debut = year ?? 1789;
  const fin = end_year ?? 1950;
  let resolution: ResolutionType = "mois";
  let corpus: CorpusType = "presse";
  if (grouping === "year") {
    resolution = "annee";
  }
  if (source === "book") {
    corpus = "livres";
  }

  try {
    const response = await fetch(
      addQueryParamsIfExist(`https://shiny.ens-paris-saclay.fr/guni/query`, {
        mot: term,
        from: debut,
        to: fin,
        resolution,
        corpus,
      })
    );
    const stringResponse = await response.text();
    const parsedCSV = Papa.parse(stringResponse, { header: true });
    let dataFrame = new DataFrame(parsedCSV.data);
    let groupedFrame: DataFrame = dataFrame;
    if (resolution === "mois" && corpus !== "livres") {
      //@ts-ignore
      groupedFrame = dataFrame
        .groupby(["annee", "mois", "gram"])
        .agg({ n: "sum", total: "sum" })
        .resetIndex();
    }
    if (resolution === "annee") {
      //@ts-ignore
      groupedFrame = dataFrame
        .groupby(["annee", "gram"])
        .agg({ n: "sum", total: "sum" })
        .resetIndex();
    }
    let rows = toJSON(groupedFrame, { format: "column" }) as GallicaGramRow[];
    rows = rows.map((row) => ({
      ...row,
      ratio: calculateRatio(row),
    }));
    return {
      data: rows.map((row) => [
        row.mois
          ? new Date(parseInt(row.annee), parseInt(row.mois) - 1).getTime()
          : new Date(parseInt(row.annee), 0).getTime(),
        row.ratio,
      ]),
      name: term,
    };
  } catch (error) {
    onNoRecordsFound(error);
    throw error;
  }
}

function calculateRatio(row: GallicaGramRow) {
  if (!row.total_sum) {
    return 0;
  }
  return row.n_sum / row.total_sum;
}

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

  const terms = searchState?.terms ?? ["brazza"];

  if (searchState) {
    data = await fetchSRU({
      ...searchState,
      terms: searchState.selected_term ? [searchState.selected_term] : terms,
      year: searchState.context_year ?? searchState.year,
      end_year: searchState.context_year ? undefined : searchState.end_year,
    });
    numResults = data.total_records;
    const response = await Promise.allSettled(
      terms?.map(
        async (term) =>
          await getSeries(
            {
              term: term,
              year: searchState.year,
              end_year: searchState.end_year,
              grouping: graphState.grouping,
              smoothing: graphState.smoothing,
              source: searchState.source,
            },
            (error) => console.error(error)
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
        <LoadingProvider>
          <GraphSeriesForm
            lineChart={<Chart series={seriesData} />}
            proximityBar={<NearbyTerms params={searchParams} />}
          />
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
        </LoadingProvider>
      </div>
    </>
  );
}
