"use client";

import React from "react";
import { GraphSeriesForm } from "./components/GraphSeriesForm";
import Head from "next/head";
import GraphContextForm from "./components/GraphContextForm";
import { fetchContext } from "./components/fetchContext";
import ContextViewer from "./components/ContextViewer";
import { useSearchState } from "./composables/useSearchState";
import { useQuery } from "react-query";
import Chart from "./components/Chart";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/design_system/card";
import { useSubmit } from "./components/LoadingProvider";
import { seriesColors } from "./components/utils/makeHighcharts";
import { components } from "./types";
import { OriginURL } from "@/src/app/context/client-fetch-context";

const strings = {
  fr: {
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
  },
  en: {
    description: "Explore word occurrences in archived Gallica periodicals.",
  },
};

export function Dashboard() {
  const translation = strings["fr"];

  const searchState = useSearchState();

  const terms = searchState?.terms ?? ["brazza"];

  const { data: contextData } = useQuery({
    queryFn: () =>
      fetchContext({
        ...searchState,
        terms: searchState.selected_term ? [searchState.selected_term] : terms,
        year: searchState.context_year ?? searchState.year ?? 1789,
        end_year: searchState.context_year ?? searchState.end_year ?? 1945,
      }),
    queryKey: ["context", searchState],
    keepPreviousData: true,
  });

  const firstRecord = contextData?.records?.[0];
  const originURL = contextData?.origin_urls?.at(0);

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
        <GraphSeriesForm>
          <div className="flex w-full justify-center">
            <Feedback />
          </div>
        </GraphSeriesForm>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="md:col-span-1">
            <TicketRow />
            <Chart />
          </div>
          <div className="md:col-span-1">
            <GraphContextForm numResults={contextData?.num_results}>
              {firstRecord ? (
                <div className="flex flex-col gap-5">
                  <OriginURL originURL={originURL} />
                  <RecordCard record={firstRecord} />
                </div>
              ) : (
                <div>Chargement...</div>
              )}
            </GraphContextForm>
          </div>
          {contextData?.records
            ?.slice(1)
            .map((record, index) => (
              <RecordCard
                key={`${record.ark}-${record.terms}-${index}`}
                record={record}
              />
            ))}
        </div>
      </div>
    </>
  );
}

// key={`${record.ark}-${record.terms}-${index}`}
function TicketRow(props: { children?: React.ReactNode }) {
  const { terms } = useSearchState();
  const { handleSubmit } = useSubmit();
  const displayTerms = terms ?? ["brazza"];
  return (
    <div className={"z-0 flex self-start m-5"}>
      <div className={"flex flex-wrap gap-10"}>
        {displayTerms?.map((term, index) => (
          <button
            onClick={() =>
              handleSubmit({
                terms: terms?.filter((t) => t !== term),
                selected_term: undefined,
              })
            }
            className={`rounded-lg border-2 bg-white p-3 text-xl shadow-md transition duration-150 hover:bg-zinc-500 hover:ease-in`}
            style={{ borderColor: seriesColors[index % seriesColors.length] }}
            key={term}
          >
            <div className={`relative h-full w-full flex flex-col`}>
              <div className={"flex flex-row gap-10"}>
                <p>{term}</p>
                <p className={"text-zinc-600"}>x</p>
              </div>
            </div>
          </button>
        ))}
      </div>
      {props.children}
    </div>
  );
}

function RecordCard(props: {
  record: components["schemas"]["RowRecordResponse"]["records"][0];
}) {
  const { record } = props;
  if (!record) {
    return null;
  }
  return (
    <Card>
      <CardHeader className="">
        <CardTitle>{record.paper_title}</CardTitle>
        <CardDescription>{record.date}</CardDescription>
      </CardHeader>
      <ContextViewer record={record} />
    </Card>
  );
}

export function Feedback() {
  return (
    <a
      href="https://github.com/gleasonw/gallica-grapher/issues"
      target="_blank"
      className="text-gray-500 underline text-sm"
    >
      Un problème ? Une suggestion ? <br />
    </a>
  );
}
