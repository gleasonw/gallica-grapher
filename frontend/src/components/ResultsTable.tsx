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
  const {
    isError,
    isLoading,
    fetchNextPage,
    fetchPreviousPage,
    hasNextPage,
    hasPreviousPage,
    ...data
  } = trpc.gallicaRecords.useInfiniteQuery(
    {
      year: props.year,
      month: props.month,
      day: props.day,
      codes: props.codes || [],
      terms: props.terms || [],
      limit: 10,
    },
    {
      getNextPageParam: (lastPage) => lastPage.nextCursor,
    }
  );

  if (isLoading || !data || !data.data || !data.data.pages[page]) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return <div>Error</div>;
  }

  const currentPage = data.data?.pages[page].data;
  console.log(currentPage);

  return (
    <div className={"flex flex-col"}>
      <div className={"m-auto ml-5 "}>{props.children}</div>
      <div className="bg-zinc-100">
        <div>
          <div className={"m-4 flex flex-col gap-5"}>
            <h1 className={"text-2xl"}>
              {currentPage && (
                <div>
                  {currentPage?.num_records_in_gallica.toLocaleString()} records
                  <div className={"flex flex-row gap-10"}>
                    {hasPreviousPage && (
                      <button
                        className={"rounded-md bg-zinc-200 p-2"}
                        onClick={() => {
                          fetchPreviousPage();
                          setPage(page - 1);
                        }}
                      >
                        Previous
                      </button>
                    )}
                    {hasNextPage && (
                      <button
                        className={"rounded-md bg-zinc-200 p-2"}
                        onClick={() => {
                          fetchNextPage();
                          setPage(page + 1);
                        }}
                      >
                        Next
                      </button>
                    )}
                  </div>
                </div>
              )}
            </h1>
            {currentPage?.records.map((record, index) => (
              <div
                key={record.url}
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
