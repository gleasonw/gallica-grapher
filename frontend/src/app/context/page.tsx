import React, { Suspense } from "react";
import { z } from "zod";
import { ContextInputForm } from "./components/ContextInputForm";
import {
  fetchContext,
  fetchSRU,
  fetchVolumeContext,
} from "../components/fetchContext";
import { ImageSnippet } from "../components/ImageSnippet";
import ContextViewer from "../components/ContextViewer";

const searchPageState = z.object({
  terms: z.string().optional(),
  year: z.coerce.number().optional(),
  end_year: z.coerce.number().optional(),
  month: z.coerce.number().optional(),
  day: z.coerce.number().optional(),
  source: z
    .literal("book")
    .or(z.literal("periodical"))
    .or(z.literal("all"))
    .optional(),
  link_term: z.string().optional(),
  link_distance: z.coerce.number().optional(),
  codes: z.string().array().optional(),
  limit: z.coerce.number().optional(),
  sort: z.literal("date").or(z.literal("relevance")).optional(),
  cursor: z.coerce.number().optional(),
});

export default async function Page({
  searchParams,
}: {
  searchParams: Record<string, any>;
}) {
  const result = searchPageState.safeParse(searchParams);
  if (!result.success) {
    return <div>Invalid search params: {result.error.message}</div>;
  }

  const params = result.data;
  const contextParams = { ...params, terms: params.terms ?? "" };
  const data = await fetchSRU(contextParams);

  const maybeNumberResults = data.total_records;
  let numResults = 0;
  if (!isNaN(maybeNumberResults) && maybeNumberResults > 0) {
    numResults = maybeNumberResults;
  }

  function getArkImageFromParams(ark: string) {
    if (Object.keys(searchParams)?.includes(`arkPage${ark}`)) {
      return searchParams[`arkPage${ark}`];
    }
  }

  return (
    <ContextInputForm params={contextParams} num_results={numResults}>
      <div className={"flex flex-col gap-20 md:m-5"}>
        {data.records?.map((record) => (
          <div
            key={record.ark}
            className={
              "border-gray-400 border md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5  w-full"
            }
          >
            <Suspense fallback={<div>Loading OCR</div>}>
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
              />
            </Suspense>
          </div>
        ))}
      </div>
    </ContextInputForm>
  );
}

export async function VolumeContext({
  ark,
  term,
  pageNum,
}: {
  ark: string;
  term: string;
  pageNum?: number;
}) {
  const volumeData = await fetchVolumeContext({ ark, term });
  return (
    <ContextViewer data={volumeData} ark={ark}>
      <Suspense
        fallback={
          <div className={"bg-gray-400 rounded h-80 w-full mb-4"}></div>
        }
        key={ark}
      >
        <ImageSnippet
          ark={ark}
          term={term}
          pageNumber={pageNum ?? volumeData[0].page_num}
        />
      </Suspense>
    </ContextViewer>
  );
}

export function ContextLoadingSkeleton() {
  return (
    <div className={"flex flex-col gap-20 md:m-5"}>
      {[...Array(10)].map((_, i) => (
        <div
          key={i}
          className={
            "animate-pulse md:border border-gray-400 md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5 items-center w-full"
          }
        >
          <div className={"text-lg bg-gray-400 rounded h-6 w-3/4 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-4 w-1/2 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-4 w-1/4 mb-4"}></div>
          <div className={"bg-gray-400 rounded h-80 w-full mb-4"}></div>
        </div>
      ))}
    </div>
  );
}
