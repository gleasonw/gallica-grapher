"use client";

import React from "react";
import { GraphSeriesForm } from "./components/GraphSeriesForm";
import Head from "next/head";
import GraphContextForm from "./components/GraphContextForm";
import { fetchContext, fetchSeries } from "./components/fetchContext";
import { NearbyTermsChart } from "./components/NearbyTermsChart";
import ContextViewer from "./components/ContextViewer";
import { ImageSnippet } from "./components/ImageSnippet";
import { useSearchState } from "./composables/useSearchState";
import { useGraphState } from "./composables/useGraphState";
import { useQuery } from "react-query";
import { useSearchParams } from "next/navigation";
import Chart from "./components/Chart";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/design_system/card";

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

  const graphState = useGraphState();

  const terms = searchState?.terms ?? ["brazza"];

  const { data: contextData, isLoading: isLoadingContext } = useQuery({
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

  const searchParams = useSearchParams();

  function getDocumentPageFromParams(ark: string): number | undefined {
    if (Object.keys(searchParams)?.includes(`arkPage${ark}`)) {
      const possibleNumber = searchParams.get(`arkPage${ark}`);
      if (possibleNumber && !isNaN(parseInt(possibleNumber))) {
        return parseInt(possibleNumber);
      }
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
        <GraphSeriesForm>
          <Chart />
        </GraphSeriesForm>
        <GraphContextForm numResults={contextData?.num_results}>
          <div className={"flex flex-col gap-20 md:m-5"}>
            {contextData?.records?.map((record, index) => (
              <Card key={`${record.ark}-${record.terms}-${index}`}>
                <CardHeader>
                  <CardTitle>{record.paper_title}</CardTitle>
                  <CardDescription>{record.date}</CardDescription>
                </CardHeader>
                <ContextViewer
                  data={record.context}
                  ark={record.ark}
                  image={
                    <ImageSnippet
                      ark={record.ark}
                      term={record.terms[0]}
                      pageNumber={
                        getDocumentPageFromParams(record.ark) ??
                        record.context[0].page_num ??
                        1
                      }
                    />
                  }
                ></ContextViewer>
              </Card>
            ))}
          </div>
        </GraphContextForm>
      </div>
    </>
  );
}
