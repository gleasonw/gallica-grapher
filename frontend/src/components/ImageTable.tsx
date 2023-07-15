import React from "react";
import { GallicaResponse } from "../models/dbStructs";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { APIargs } from "./OCRTable";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import Image from "next/image";
import { QueryPagination } from "./QueryPagination";
import { ContextProps } from "./OccurrenceContext";

async function fetchImages(args: APIargs) {
  const url = addQueryParamsIfExist(
    "https://gallica-grapher.ew.r.appspot.com/api/gallicaRecords",
    { ...args, row_split: true }
  );
  const response = await fetch(url);
  return (await response.json()) as GallicaResponse;
}

export function ImageTable({
  codes,
  terms,
  yearRange,
  month,
  source,
  link_term,
  link_distance,
  selectedPage,
  onSelectedPageChange,
}: ContextProps & {
  selectedPage: number;
  onSelectedPageChange: (page: number) => void;
}) {
  const limit = 10;
  const { data, isLoading, isRefetching } = useQuery({
    queryKey: [
      "gallicaRecords",
      {
        yearRange,
        month,
        codes,
        terms,
        source,
        link_term,
        link_distance,
        selectedPage,
      },
    ],
    queryFn: () =>
      fetchImages({
        terms,
        codes,
        month,
        source,
        link_term,
        link_distance,
        cursor: (selectedPage - 1) * (limit ? limit : 10),
        yearRange,
        end_year: month ? undefined : yearRange?.[1],
      }),
    keepPreviousData: true,
    staleTime: Infinity,
  });

  const total_results = Number(data?.num_results) ?? 0;
  const cursorMax = Math.floor(total_results / 10);

  if (isLoading || isRefetching) {
    return (
      <div className={"flex flex-col gap-20 md:m-5"}>
        {[...Array(10)].map((_, i) => (
          <div
            key={i}
            className={
              "animate-pulse md:border border-gray-400 md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5 items-center"
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
  } else {
    return (
      <>
        <QueryPagination
          selectedPage={selectedPage}
          cursorMax={cursorMax}
          onChange={onSelectedPageChange}
        />
        <div className={"flex flex-col gap-20 md:m-5"}>
          {data?.records?.map((record) => (
            <div
              key={record.ark}
              className={
                "md:border border-gray-400 md:shadow-lg md:rounded-lg md:p-10 flex flex-col gap-5 items-center"
              }
            >
              <h2 className={"text-lg"}>{record.paper_title}</h2>
              <h3>{record.author}</h3>
              <h4>{record.date}</h4>
              <ImageSnippet
                ark={record.ark}
                term={terms?.[0] ?? ""}
                url={record.context?.[0]?.page_url ?? ""}
              />
            </div>
          ))}
        </div>
      </>
    );
  }
}

function ImageSnippet({
  ark,
  term,
  url,
}: {
  ark: string;
  term: string;
  url: string;
}) {
  const last_el = url.split("/").pop();
  const page_sec = last_el?.split(".")?.[0];
  const page = page_sec?.slice(1);

  async function doFetch() {
    const url = addQueryParamsIfExist(
      `https://gallica-grapher-production.up.railway.app/api/image`,
      {
        ark: ark,
        term: term,
        page: page,
      }
    );
    const response = await fetch(url);
    const imgString = (await response.json()) as { image: string };
    return imgString;
  }

  const { data, isLoading } = useQuery({
    queryKey: ["imageSnippet", { ark: ark, term: term }],
    queryFn: doFetch,
    keepPreviousData: true,
    staleTime: Infinity,
  });

  return isLoading ? (
    <div
      className={"bg-gray-400 rounded h-80 w-full mb-4 animate-pulse border"}
    />
  ) : (
    <Link href={url} target={"_blank"}>
      <Image src={data?.image ?? ""} alt={term} width={700} height={80} />
    </Link>
  );
}
