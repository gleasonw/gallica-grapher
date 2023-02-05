import React from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { Context } from "./Context";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { GallicaResponse } from "../models/dbStructs";
import { apiURL } from "./apiURL";

export interface TableProps {
  terms?: string[];
  codes?: string[];
  day?: number | null;
  month?: number | null;
  year?: number | null;
  source?: "book" | "periodical" | "all" | null;
  link_term?: string | null;
  link_distance?: number | null;
  children?: React.ReactNode;
  limit: number;
  sort?: "date" | "relevance" | null;
  initialRecords?: Awaited<ReturnType<typeof fetchContext>>;
}

export const fetchContext = async ({ pageParam = 0 }, props: TableProps) => {
  let baseUrl = `${apiURL}/api/gallicaRecords`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...props,
    children: undefined,
    initialRecords: undefined,
    cursor: pageParam,
    limit: props.limit,
  });
  const response = await fetch(url);
  const data = (await response.json()) as GallicaResponse;
  let nextCursor = null;
  let previousCursor = pageParam ?? 0;
  if (data.records && data.records.length > 0) {
    if (pageParam) {
      nextCursor = pageParam + props.limit;
    } else {
      nextCursor = props.limit;
    }
  }
  return {
    data,
    nextCursor,
    previousCursor,
  };
};

export function ResultsTable(props: TableProps) {
  const [selectedPage, setSelectedPage] = React.useState(1);
  const limit = props.limit || 10;

  let ssrData;
  if (props.initialRecords) {
    ssrData = {
      pages: [props.initialRecords],
      pageParams: [0],
    };
  } else {
    ssrData = undefined;
  }
  const {
    isFetching,
    isError,
    isLoading,
    fetchNextPage,
    fetchPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
    ...data
  } = useInfiniteQuery({
    queryKey: [
      "context",
      props.year,
      props.month,
      props.day,
      props.codes,
      props.terms,
      props.source,
      props.link_term,
      props.link_distance,
      props.limit,
      props.sort,
    ],
    queryFn: (pageParams) =>
      fetchContext(pageParams, { ...props, children: undefined }),
    staleTime: Infinity,
    keepPreviousData: true,
    placeholderData: ssrData,
  });

  React.useEffect(() => {
    setSelectedPage(1);
  }, [props]);

  if (isError) {
    return <div>Error</div>;
  }

  const currentPage = data.data?.pages.filter(
    (page) => page?.nextCursor == pageToCursor(selectedPage)
  )[0];
  const total_results = Number(data.data?.pages[0]?.data.num_results) ?? 0;
  const origin_urls = data.data?.pages[0]?.data.origin_urls ?? [];
  const cursorMax = Math.floor(total_results / limit) + 1;
  const fetchedCursors = data.data?.pages.map((page) => page?.nextCursor);
  const fetchedSet = new Set(fetchedCursors);

  async function handleCursorIncrement(amount: number = 1) {
    if (fetchedSet && !fetchedSet.has(pageToCursor(selectedPage + amount))) {
      await fetchNextPage({
        pageParam: pageToCursor(selectedPage + amount - 1),
      });
    }
    setSelectedPage(selectedPage + amount);
  }

  async function handleCursorDecrement(amount: number = 1) {
    if (fetchedSet && !fetchedSet.has(pageToCursor(selectedPage - amount))) {
      await fetchPreviousPage({
        pageParam: pageToCursor(selectedPage - (amount + 1)),
      });
    }
    setSelectedPage(selectedPage - amount);
  }

  function pageToCursor(page: number) {
    return page * props.limit;
  }

  return (
    <div className={"mb-20 flex flex-col"}>
      <div className="">
        <div>
          <div className={"mt-5 flex flex-col gap-5"}>
            <div className={"m-auto ml-5 "}>{props.children}</div>
            <h1 className={"ml-10 text-2xl"}>
              {!isFetchingNextPage && !isFetchingPreviousPage && isFetching && (
                <p>Fetching updated context...</p>
              )}
              {!currentPage && !isFetching && <p>No results found</p>}
              {currentPage && (
                <div className={"flex flex-row gap-10"}>
                  {total_results.toLocaleString()} results
                </div>
              )}
            </h1>
            {currentPage?.data.records.map((record, index) => (
              <div
                key={index}
                className={"flex flex-col gap-5 bg-white p-5 shadow-md"}
              >
                <div className={"flex flex-row flex-wrap gap-10 pb-5 text-lg"}>
                  <p>{record.terms.join(", ")}</p>
                  <p>{record.date}</p>
                  <p>{record.paper_title}</p>
                  <a
                    className={"truncate underline"}
                    href={record.url}
                    target={"_blank"}
                    rel={"noreferrer"}
                  >
                    {record.url}
                  </a>
                </div>
                <Context record={record} />
              </div>
            ))}
            {isFetchingNextPage && <p>Fetching next page...</p>}
            {isFetchingPreviousPage && <p>Fetching previous page...</p>}
            {currentPage && !isFetchingNextPage && !isFetchingPreviousPage && (
              <div>
                <div
                  className={
                    "flex flex-row justify-center gap-10 text-xl md:text-3xl lg:text-3xl"
                  }
                >
                  {selectedPage != 1 && (
                    <div className={"flex flex-row gap-10"}>
                      <button
                        onClick={() => handleCursorDecrement(selectedPage - 1)}
                      >
                        {"<<"}
                      </button>
                      <button onClick={() => handleCursorDecrement()}>
                        {"<"}
                      </button>
                    </div>
                  )}
                  <CursorInput
                    cursor={selectedPage}
                    cursorMax={cursorMax}
                    onCursorIncrement={handleCursorIncrement}
                    onCursorDecrement={handleCursorDecrement}
                  />
                  <p>of {cursorMax.toLocaleString()}</p>
                  {selectedPage !== cursorMax && (
                    <div className={"flex flex-row gap-10"}>
                      <button onClick={() => handleCursorIncrement()}>
                        {">"}
                      </button>
                      <button
                        onClick={() =>
                          handleCursorIncrement(cursorMax - selectedPage)
                        }
                      >
                        {">>"}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

interface CursorInputProps {
  cursor: number;
  cursorMax: number;
  onCursorIncrement: (amount?: number) => void;
  onCursorDecrement: (amount?: number) => void;
}

function CursorInput(props: CursorInputProps) {
  const [localCursor, setLocalCursor] = React.useState(props.cursor);

  React.useEffect(() => {
    setLocalCursor(props.cursor);
  }, [props.cursor]);

  const handleLocalCursorChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = Number(e.target.value);

    let valueToPropagate = value;

    if (value > props.cursorMax) {
      valueToPropagate = props.cursorMax;
    }

    if (value <= 0) {
      valueToPropagate = 1;
    }

    if (valueToPropagate > props.cursor) {
      props.onCursorIncrement(valueToPropagate - props.cursor);
    } else if (valueToPropagate < props.cursor) {
      props.onCursorDecrement(props.cursor - valueToPropagate);
    }
    setLocalCursor(valueToPropagate);
  };

  return (
    <input
      type={"number"}
      value={localCursor}
      onChange={(e) => setLocalCursor(e.target.valueAsNumber)}
      className={"w-10"}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleLocalCursorChange(e as any);
        }
      }}
    />
  );
}
