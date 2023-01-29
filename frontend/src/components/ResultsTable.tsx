import React from "react";
import { trpc } from "../utils/trpc";
import { Context } from "./Context";

export interface TableProps {
  terms?: string[];
  codes?: string[];
  day?: number;
  month?: number;
  year?: number;
  children?: React.ReactNode;
}

export const ResultsTable: React.FC<TableProps> = (props) => {
  const [page, setPage] = React.useState(0);
  const [selectedCursor, setSelectedCursor] = React.useState(0);
  const {
    isError,
    isLoading,
    fetchNextPage,
    fetchPreviousPage,
    hasNextPage,
    hasPreviousPage,
    isFetchingNextPage,
    ...data
  } = trpc.gallicaRecords.useInfiniteQuery(
    {
      year: props.year,
      month: props.month,
      day: props.day,
      codes: props.codes || [],
      terms: props.terms || [],
      limit: 20,
    },
    {
      getNextPageParam: (lastPage) => lastPage.nextCursor,
      getPreviousPageParam: (firstPage) => firstPage.previousCursor,
      staleTime: Infinity,
    }
  );

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return <div>Error</div>;
  }
  const currentPage = data.data?.pages.filter(
    (page) => page.previousCursor == selectedCursor
  )[0];
  const total_results = Number(data.data?.pages[0].data.num_results) ?? 0;
  console.log(data.data?.pages);
  const fetchedCursors = data.data?.pages.map((page) => page.previousCursor);

  async function handleCursorChange() {
    //figure out if we need to fetch the next page
    if (fetchedCursors && hasNextPage && !fetchedCursors.includes(selectedCursor + 20)) {
      await fetchNextPage();
    }
    setSelectedCursor(selectedCursor + 20);
  }

  return (
    <div className={"flex flex-col"}>
      <div className={"m-auto ml-5 "}>{props.children}</div>
      <div className="bg-zinc-100">
        <div>
          <div className={"m-4 flex flex-col gap-5"}>
            <h1 className={"text-2xl"}>
              {isFetchingNextPage && <p>Fetching next page...</p>}
              {currentPage && (
                <div>
                  <div className={"flex flex-row gap-10"}>
                    {hasPreviousPage && selectedCursor != 0 && (
                      <button
                        onClick={() => setSelectedCursor(selectedCursor - 20)}
                      >
                        {"<"}
                      </button>
                    )}
                    <input
                      type={"number"}
                      value={selectedCursor / 20 + 1}
                      onChange={async (e) => {
                        const value = Number(e.target.value);
                        if (value !== undefined && value > 0) {
                          if (value > page + 1) {
                            if (value == page + 2) {
                              handleCursorChange();
                            } else {
                              await fetchNextPage({ pageParam: value * 20 });
                              setSelectedCursor((value - 1) * 20);
                            }
                          } else {
                            setSelectedCursor((value-1) * 20);
                          }
                        }
                      }}
                    />
                    <p>of {Math.floor(total_results / 20).toLocaleString()}</p>
                    {hasNextPage && (
                      <button onClick={() => handleCursorChange()}>
                        {">"}
                      </button>
                    )}
                  </div>
                </div>
              )}
            </h1>
            {currentPage?.data.records.map((record, index) => (
              <div
                key={index}
                className={"flex flex-col gap-5 bg-white p-5 shadow-md"}
              >
                <div className={"flex flex-row flex-wrap gap-10 pb-5 text-lg"}>
                  <p>{record.term}</p>
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
          </div>
        </div>
      </div>
    </div>
  );
};
