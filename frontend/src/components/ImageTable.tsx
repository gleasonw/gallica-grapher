import React from "react";
import { GallicaImageResponse, GallicaResponse } from "../models/dbStructs";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { TableProps } from "./OCRTable";
import { APIargs } from "./OCRTable";
import { useQuery } from "@tanstack/react-query";
import Image from "next/image";
import { QueryPagination } from "./QueryPagination";
import { CursorInput } from "./CursorInput";

async function fetchImages(args: APIargs) {
  const url = addQueryParamsIfExist(
    "http://localhost:8000/api/gallicaRecords/image",
    args
  );
  const response = await fetch(url);
  return (await response.json()) as GallicaImageResponse;
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

  const { data, isLoading } = useQuery({
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
  });

  console.log(data);
  const total_results = Number(data?.num_results) ?? 0;
  console.log(total_results);
  const cursorMax = Math.floor(total_results / 10);

  return (
    <>
      {selectedPage}
      {isLoading && <div>Loading...</div>}

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
            {record.context.map((context) => (
              <span key={context.page}>
                <Image
                  src={context.image}
                  alt={context.term}
                  width={700}
                  height={80}
                />
              </span>
            ))}
          </div>
        ))}
      </div>
    </>
  );
}
