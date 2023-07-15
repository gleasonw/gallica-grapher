import React from "react";
import { GallicaImageResponse, GallicaResponse } from "../models/dbStructs";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { TableProps } from "./OCRTable";
import { APIargs } from "./OCRTable";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import Image from "next/image";
import { QueryPagination } from "./QueryPagination";
import { CursorInput } from "./CursorInput";

async function fetchImages(args: APIargs) {
  const url = addQueryParamsIfExist(
    "http://localhost:8000/api/gallicaRecords",
    { ...args, row_split: true }
  );
  const response = await fetch(url);
  return (await response.json()) as GallicaResponse;
}

export function ImageTable(props: TableProps) {
  const [selectedPage, setSelectedPage] = React.useState(1);

  const {
    yearRange,
    month,
    day,
    codes,
    terms,
    source,
    link_term,
    link_distance,
    sort,
  } = props;

  const { data, isLoading, isRefetching } = useQuery({
    queryKey: [
      "gallicaRecords",
      {
        yearRange,
        month,
        day,
        codes,
        terms,
        source,
        link_term,
        link_distance,
        sort,
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
        sort,
        cursor: (selectedPage - 1) * (props.limit ? props.limit : 10),
        limit: props.limit,
        year: props.yearRange?.[0],
        end_year: month ? undefined : props.yearRange?.[1],
      }),
    keepPreviousData: true,
    staleTime: Infinity,
  });

  console.log(data);
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
          onPageIncrement={() => setSelectedPage(selectedPage + 1)}
          onPageDecrement={() => setSelectedPage(selectedPage - 1)}
          selectedPage={selectedPage}
          cursorMax={cursorMax}
          onLastPage={() => setSelectedPage(cursorMax + 1)}
          onFirstPage={() => setSelectedPage(1)}
        >
          <p className={"mr-3 md:mr-5 lg:mr-5"}>Page</p>
          <CursorInput
            cursor={selectedPage}
            cursorMax={cursorMax}
            onCursorIncrement={setSelectedPage}
            onCursorDecrement={setSelectedPage}
            key={selectedPage}
          />
          <p className={"ml-3 md:ml-5 lg:ml-5"}>/ {cursorMax + 1}</p>
        </QueryPagination>
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
                term={props.terms?.[0] ?? ""}
                url={record.context?.[0]?.page_url ?? ""}
              />
            </div>
          ))}
        </div>
      </>
    );
  }
}

function ImageSnippet(props: { ark: string; term: string; url: string }) {
  const last_el = props.url.split("/").pop();
  const page_sec = last_el?.split(".")?.[0];
  const page = page_sec?.slice(1);

  async function doFetch() {
    const url = addQueryParamsIfExist(
      `https://gallica-grapher-production.up.railway.app/api/image`,
      {
        ark: props.ark,
        term: props.term,
        page: page,
      }
    );
    const response = await fetch(url);
    const imgString = (await response.json()) as { image: string };
    return imgString;
  }

  const { data, isLoading } = useQuery({
    queryKey: ["imageSnippet", { ark: props.ark, term: props.term }],
    queryFn: doFetch,
    keepPreviousData: true,
    staleTime: Infinity,
  });

  return isLoading ? (
    <div
      className={"bg-gray-400 rounded h-80 w-full mb-4 animate-pulse border"}
    />
  ) : (
    <Link href={props.url} target={"_blank"}>
      <Image src={data?.image ?? ""} alt={props.term} width={700} height={80} />
    </Link>
  );
}
