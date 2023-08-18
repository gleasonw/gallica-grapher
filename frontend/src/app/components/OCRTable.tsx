import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Cell,
  Row,
  TableInstance,
  useExpanded,
  useGroupBy,
  useTable,
} from "react-table";
import { useContext } from "react";
import { LangContext } from "./LangContext";
import { Spinner } from "./Spinner";
import { QueryPagination } from "./QueryPagination";
import { fetchContext } from "./fetchContext";

export type ContextProps = {
  terms?: string[];
  link_term?: string;
  link_distance?: number;
  codes?: string[];
  month?: number;
  yearRange?: [number?, number?];
  source?: "periodical" | "book" | "all";
  all_context?: boolean;
  children: React.ReactNode;
};

export function OCRTable({
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
  children: React.ReactNode;
}) {
  const { lang } = useContext(LangContext);
  const charLimit = 70;
  const limit = 10;

  // this will be used to check if we can use ssr data... maybe a better way?
  const currentFetchParams = {
    yearRange,
    month,
    codes,
    terms,
    source,
    link_term,
    link_distance,
    selectedPage,
    limit,
  };

  const { isFetching, data } = useQuery({
    queryKey: [
      "context",
      yearRange,
      month,
      codes,
      terms,
      source,
      link_term,
      link_distance,
      selectedPage,
      limit,
    ],
    queryFn: () =>
      fetchContext({
        terms: terms ?? [],
        codes,
        month,
        source: source ?? "all",
        link_term,
        link_distance,
        cursor: (selectedPage - 1) * (limit ? limit : 10),
        year: yearRange?.[0],
        end_year: month ? undefined : yearRange?.[1],
      }),
    staleTime: Infinity,
  });

  const tableData = React.useMemo(
    () =>
      data?.records
        ?.map((record) => {
          const documentMeta = {
            document: `${record.paper_title}||${record.date}||${record.url}`,
            date: record.date,
          };
          if (record.context.length === 0) {
            return [
              {
                ...documentMeta,
                page: (
                  <a
                    href={record.url}
                    target={"_blank"}
                    rel={"noreferrer"}
                    className={"font-medium underline"}
                  >
                    {record.url}
                  </a>
                ),
                left_context: "",
                pivot: "Unable to connect to Gallica's ContentSearch API",
                right_context: "",
              },
            ];
          }
          return record.context.map((contextRow) => ({
            ...documentMeta,
            page: (
              <div className={"flex"}>
                <a
                  className="underline font-medium p-2"
                  href={contextRow.page_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Image
                </a>
              </div>
            ),
            left_context: contextRow.left_context,
            pivot: (
              <span className={"text-blue-500 font-medium"}>
                {contextRow.pivot}
              </span>
            ),
            right_context: contextRow.right_context,
          }));
        })
        .flat() ?? [],
    [data]
  );

  function showFirstWhenAggregated({ value }: { value: string[] }) {
    return value[0];
  }

  const columns = React.useMemo(
    () => [
      {
        Header: "Document",
        accessor: "document",
        Cell: ({ value }: { value: string }) => (
          <div className={""}>
            {value
              .split("||")
              .slice(0, 2)
              .map((v, i) =>
                i === 0 ? (
                  <div className="italic" key={v}>
                    {v}
                  </div>
                ) : (
                  <div key={v}>{v}</div>
                )
              )}
          </div>
        ),
      } as const,
      {
        Header: "Gallica",
        accessor: "page",
        aggregate: "unique",
        Aggregated: showFirstWhenAggregated,
      } as const,
      {
        Header: lang === "fr" ? "Contexte gauche" : "Left context",
        accessor: "left_context" as const,
        aggregate: "unique",
        Aggregated: showFirstWhenAggregated,
      } as const,
      {
        Header: "Pivot",
        accessor: "pivot",
        aggregate: "unique",
        Aggregated: showFirstWhenAggregated,
      } as const,
      {
        Header: lang === "fr" ? "Contexte droit" : "Right context",
        accessor: "right_context",
        aggregate: "unique",
        Aggregated: showFirstWhenAggregated,
      } as const,
    ],
    [lang]
  );

  const tableInstance = useTable(
    {
      columns,
      data: tableData,
      // @ts-ignore
      initialState: { groupBy: ["document"] },
    },
    useGroupBy,
    useExpanded
  );
  const total_results = Number(data?.num_results) ?? 0;
  const cursorMax = Math.floor(total_results / limit);

  return (
    <div className={" flex flex-col justify-center mb-20"}>
      {tableInstance.data.length > 0 ? (
        <div>
          <div className={"ml-5 flex flex-col mb-2"}>
            <QueryPagination
              selectedPage={selectedPage}
              cursorMax={cursorMax}
              onChange={onSelectedPageChange}
            />
            <Spinner isFetching={isFetching} />
          </div>
          <div>
            <DesktopTable tableInstance={tableInstance} />
            <MobileTable tableInstance={tableInstance} />
          </div>
        </div>
      ) : isFetching ? (
        <div
          className={
            "bg-gray-400 h-96 rounded w-full mb-4 animate-pulse border m-10"
          }
        />
      ) : (
        <p className={"text-center"}>
          No results for these params (or unable to connect to Gallica)
        </p>
      )}
    </div>
  );
}

function MobileTable(props: { tableInstance: TableInstance<any> }) {
  return (
    <div className={"flex flex-col gap-10 md:hidden lg:hidden"}>
      {props.tableInstance.rows.map((row, index) => {
        props.tableInstance.prepareRow(row);
        return (
          <div
            {...row.getRowProps()}
            // @ts-ignore
            {...row.getToggleRowExpandedProps()}
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
                  {cellRender(row, cell)}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

function DesktopTable(props: { tableInstance: TableInstance<any> }) {
  return (
    <table
      className={
        "shadow-xl rounded-xl border hidden md:table lg:table xl:table transition-all duration-300 max-w-full table-auto w-full"
      }
    >
      <thead>
        {props.tableInstance.headerGroups.map((headerGroup, index) => (
          <tr {...headerGroup.getHeaderGroupProps()} key={index}>
            {headerGroup.headers.map((column, index) => (
              <th
                {...column.getHeaderProps()}
                key={index}
                className={"pb-2 pt-2 font-medium"}
              >
                {column.render("Header")}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...props.tableInstance.getTableBodyProps()} className={""}>
        {props.tableInstance.rows.map((row, index) => {
          props.tableInstance.prepareRow(row);
          return (
            <tr
              {...row.getRowProps()}
              className={"odd:bg-zinc-100 w-full"}
              {
                // @ts-ignore
                ...row.getToggleRowExpandedProps()
              }
              key={index}
            >
              {row.cells.map((cell, index) => {
                let twStyle = "";
                if (
                  cell.column.Header === "Left context" ||
                  cell.column.Header === "Contexte gauche"
                ) {
                  twStyle = " text-right";
                }
                // @ts-ignore
                if (cell.column.Header === "Document" && !row.isExpanded) {
                  twStyle = " max-w-xs truncate";
                }
                return (
                  <td
                    {...cell.getCellProps()}
                    key={index}
                    className={"pl-4 pr-4 pt-2 pb-2" + twStyle}
                  >
                    {cellRender(row, cell)}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

//TODO: move type defs to vercel to remove ts-ignore
function cellRender(row: Row, cell: Cell) {
  return (
    // @ts-ignore
    cell.isGrouped ? (
      // If it's a grouped cell, add an expander and row count
      <div className={"flex gap-3"}>
        <span className={"text-xl"}>
          {
            // @ts-ignore
            row.isExpanded ? "⌄" : "›"
          }
        </span>{" "}
        ({row.subRows.length}) {cell.render("Cell")}
      </div>
    ) : // @ts-ignore
    cell.isAggregated ? (
      // If the cell is aggregated, use the Aggregated
      // renderer for cell
      // @ts-ignore
      row.isExpanded ? (
        cell.column.id === "date" ? (
          cell.render("Cell")
        ) : null
      ) : (
        cell.render("Aggregated")
      )
    ) : // @ts-ignore
    cell.isPlaceholder ? null : cell.column.id !== "date" ? ( // Otherwise, just render the regular cell // For cells with repeated values, render null
      cell.render("Cell")
    ) : null
  );
}
