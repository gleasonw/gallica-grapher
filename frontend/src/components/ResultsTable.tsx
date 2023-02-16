import React from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { Column, useTable } from "react-table";
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
    row_split: true,
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

  const columns: Column<{
    col1: JSX.Element;
    col2: string;
    col3: string;
    col4: JSX.Element;
    col5: string;
  }>[] = React.useMemo(
    () => [
      {
        Header: "Document",
        accessor: "col1",
      },
      {
        Header: "Date",
        accessor: "col2",
      },
      {
        Header: "Left context",
        accessor: "col3",
      },
      {
        Header: "Pivot",
        accessor: "col4",
      },
      {
        Header: "Right context",
        accessor: "col5",
      },
    ],
    []
  );

  const currentPage = data.data?.pages.filter(
    (page) => page?.nextCursor == pageToCursor(selectedPage)
  )[0];

  const tableData = React.useMemo(
    () =>
      currentPage?.data.records
        .map((record) =>
          record.context.map((contextRow) => ({
            col1: (
              <a
                href={record.url}
                className={"underline"}
                target={"_blank"}
                rel="noreferrer"
              >
                {record.paper_title}
              </a>
            ),
            col2: record.date,
            col3: contextRow.left_context,
            col4: <span className={"font-medium"}>{contextRow.pivot}</span>,
            col5: contextRow.right_context,
          }))
        )
        .flat() ?? [],
    [currentPage]
  );

  const tableInstance = useTable({ columns, data: tableData });

  const total_results = Number(data.data?.pages[0]?.data.num_results) ?? 0;
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
      <div className={"mt-5 flex flex-col gap-5 justify-center"}>
        <h1 className={"text-2xl flex flex-col gap-2 ml-5"}>
          {!isFetchingNextPage && !isFetchingPreviousPage && isFetching && (
            <p>Fetching updated context...</p>
          )}
          {!currentPage && !isFetching && <p>No results found</p>}
          {currentPage && (
            <div className={"flex flex-row gap-10"}>
              {total_results.toLocaleString()} total documents
            </div>
          )}
          <p className={"text-xl"}>5 documents per page</p>
          {isFetchingNextPage && <p>Fetching next page...</p>}
          {isFetchingPreviousPage && <p>Fetching previous page...</p>}
        </h1>
        {currentPage && !isFetchingNextPage && !isFetchingPreviousPage && (
          <div
            className={
              "flex flex-row justify-center items-center text-xl md:text-2xl lg:text-2xl md:ml-5 lg:ml-5"
            }
          >
            {selectedPage != 1 && (
              <div className={"flex flex-row justify-between"}>
                <button
                  onClick={() => handleCursorDecrement(selectedPage - 1)}
                  className={"p-3"}
                >
                  {"<<"}
                </button>
                <button
                  className={"p-4"}
                  onClick={() => handleCursorDecrement()}
                >
                  {"<"}
                </button>
              </div>
            )}
            <p className={"md:mr-5 lg:mr-5"}>Page</p>
            <CursorInput
              cursor={selectedPage}
              cursorMax={cursorMax}
              onCursorIncrement={handleCursorIncrement}
              onCursorDecrement={handleCursorDecrement}
            />
            <p className={"md:ml-5 lg:ml-5"}>of {cursorMax.toLocaleString()}</p>
            {selectedPage !== cursorMax && (
              <div className={"flex flex-row justify-between"}>
                <button
                  className={"p-4"}
                  onClick={() => handleCursorIncrement()}
                >
                  {">"}
                </button>
                <button
                  onClick={() =>
                    handleCursorIncrement(cursorMax - selectedPage)
                  }
                  className={"p-3"}
                >
                  {">>"}
                </button>
              </div>
            )}
          </div>
        )}
        <div className={"m-auto ml-5 "}>{props.children}</div>
        <table className={"shadow-md hidden md:block lg:block"}>
          <thead>
            {tableInstance.headerGroups.map((headerGroup, index) => (
              <tr {...headerGroup.getHeaderGroupProps()} key={index}>
                {headerGroup.headers.map((column, index) => (
                  <th {...column.getHeaderProps()} key={index}>
                    {column.render("Header")}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody {...tableInstance.getTableBodyProps()}>
            {tableInstance.rows.map((row, index) => {
              tableInstance.prepareRow(row);
              return (
                <tr
                  {...row.getRowProps()}
                  key={index}
                  className={"odd:bg-zinc-100"}
                >
                  {row.cells.map((cell, index) => {
                    let twStyle = "";
                    if (cell.column.Header === "Left context") {
                      twStyle = "text-right";
                    }
                    return (
                      <td
                        {...cell.getCellProps()}
                        key={index}
                        className={"pl-5 pr-5 pt-2 pb-2 " + twStyle}
                      >
                        {cell.render("Cell")}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
        <div className={"flex flex-col gap-10 md:hidden lg:hidden"}>
          {tableInstance.rows.map((row, index) => {
            tableInstance.prepareRow(row);
            return (
              <div
                {...row.getRowProps()}
                key={index}
                className={"odd:bg-zinc-100"}
              >
                {row.cells.map((cell, index) => {
                  return (
                    <div
                      {...cell.getCellProps()}
                      key={index}
                      className={"pl-5 pr-5 pt-2 pb-2 "}
                    >
                      {cell.render("Cell")}
                    </div>
                  );
                })}
              </div>
            );
          })}
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
      className={"w-full max-w-max border rounded-md"}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          handleLocalCursorChange(e as any);
        }
      }}
    />
  );
}
