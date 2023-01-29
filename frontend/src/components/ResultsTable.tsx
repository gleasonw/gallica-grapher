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
  const [selectedPage, setSelectedPage] = React.useState(1);
  const {
    isError,
    isLoading,
    fetchNextPage,
    fetchPreviousPage,
    hasNextPage,
    hasPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
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
      //TODO: fix this logic, it's never really used since the cursor is not continuous
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
    (page) => page.nextCursor == pageToCursor(selectedPage)
  )[0];
  const total_results = Number(data.data?.pages[0].data.num_results) ?? 0;

  // TODO: Make this a set... I don't think the perf will matter much, but a nice touch
  const fetchedCursors = data.data?.pages.map((page) => page.nextCursor);

  async function handleCursorIncrement(amount: number = 1) {
    if (
      fetchedCursors &&
      hasNextPage &&
      !fetchedCursors.includes(pageToCursor(selectedPage + amount))
    ) {
      await fetchNextPage({
        pageParam: pageToCursor(selectedPage + amount - 1),
      });
    }
    setSelectedPage(selectedPage + amount);
  }

  async function handleCursorDecrement(amount: number = 1) {
    if (
      fetchedCursors &&
      hasPreviousPage &&
      !fetchedCursors.includes(pageToCursor(selectedPage - amount))
    ) {
      await fetchPreviousPage({
        pageParam: pageToCursor(selectedPage - (amount + 1)),
      });
    }
    setSelectedPage(selectedPage - amount);
  }

  function pageToCursor(page: number) {
    return page * 20;
  }

  console.log(data.data.pages);

  return (
    <div className={"flex flex-col"}>
      <div className={"m-auto ml-5 "}>{props.children}</div>
      <div className="bg-zinc-100">
        <div>
          <div className={"m-4 flex flex-col gap-5"}>
            <h1 className={"text-2xl"}>
              {isFetchingNextPage && <p>Fetching next page...</p>}
              {isFetchingPreviousPage && <p>Fetching previous page...</p>}
              {currentPage && (
                <div>
                  <div className={"flex flex-row justify-center gap-10"}>
                    {hasPreviousPage && selectedPage != 1 && (
                      <button onClick={() => handleCursorDecrement()}>
                        {"<"}
                      </button>
                    )}
                    <input
                      type={"number"}
                      value={selectedPage}
                      onChange={async (e) => {
                        const value = Number(e.target.value);
                        if (value !== undefined && value > 0) {
                          if (value > selectedPage) {
                            handleCursorIncrement(value - selectedPage);
                          } else if (value < selectedPage) {
                            handleCursorDecrement(selectedPage - value);
                          }
                        }
                      }}
                    />
                    <p>of {Math.floor(total_results / 20).toLocaleString()}</p>
                    {hasNextPage && (
                      <button onClick={() => handleCursorIncrement()}>
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
