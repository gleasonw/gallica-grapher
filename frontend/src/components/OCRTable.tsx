import React from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Cell,
  Row,
  TableInstance,
  useExpanded,
  useGroupBy,
  useTable,
} from "react-table";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { GallicaResponse } from "../models/dbStructs";
import { useContext } from "react";
import { LangContext } from "./LangContext";
import { apiURL } from "./apiURL";
import allAinB from "./utils/objectsEqual";
import { Spinner } from "./Spinner";
import { StaticPropContext } from "./StaticPropContext";
import { QueryPagination } from "./QueryPagination";
import { CursorInput } from "./CursorInput";

export interface TableProps {
  terms?: string[];
  codes?: string[];
  day?: number;
  month?: number;
  yearRange?: [number | undefined, number | undefined];
  source?: "book" | "periodical" | "all";
  link_term?: string;
  link_distance?: number;
  children?: React.ReactNode;
  limit?: number;
  sort?: "date" | "relevance";
  all_context?: boolean;
}

export type APIargs = Omit<TableProps, "children" | "initialRecords"> & {
  cursor?: number;
  year?: number;
  end_year?: number;
};

export async function fetchContext(args: APIargs) {
  let baseUrl = `https://gallica-grapher.ew.r.appspot.com/api/gallicaRecords`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
    all_context: args.all_context,
    row_split: true,
  });
  console.log(url);
  const response = await fetch(url);
  return (await response.json()) as GallicaResponse;
}

async function fetchCustomWindowContext(args: APIargs, window: number) {
  let baseUrl = `https://gallica-grapher.ew.r.appspot.com/api/customWindowGallicaRecords`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
    window_size: window,
  });
  const response = await fetch(url);
  return (await response.json()) as GallicaResponse;
}

export function OCRTable(props: TableProps) {
  const [selectedPage, setSelectedPage] = React.useState(1);
  const [customWindow, setCustomWindow] = React.useState<number>(0);
  const limit = props.limit || 10;
  const { lang } = useContext(LangContext);
  const strings = {
    fr: {
      noResults: "Aucun résultat",
      loading_next: "Chargement de la prochaine page...",
      loading_previous: "Chargement de la page précédente...",
      error: "Erreur",
      total_docs: "documents",
      num_docs_page: `Les occurrences dans ${limit} documents sont affichées`,
      group_by_doc: "Regrouper par document",
      ungroup_by_doc: "Dégrouper par document",
      download_csv: "Télécharger page CSV",
    },
    en: {
      noResults: "No results",
      loading_next: "Loading next page...",
      loading_previous: "Loading previous page...",
      error: "Error",
      total_docs: "documents",
      num_docs_page: `Occurrences in ${limit} documents are displayed`,
      group_by_doc: "Group by document",
      ungroup_by_doc: "Ungroup by document",
      download_csv: "Download CSV page",
    },
  };
  const charLimit = 70;

  React.useEffect(() => {
    setSelectedPage(1);
  }, [props.terms]);

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

  // this will be used to check if we can use ssr data... maybe a better way?
  const currentFetchParams = {
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
    limit,
    customWindow,
  };

  const staticData = useContext(StaticPropContext);

  const { isFetching, data } = useQuery({
    queryKey: [
      "context",
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
        limit,
        customWindow,
      },
    ],
    queryFn: () => {
      const apiArgs: APIargs = {
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
      };
      if (customWindow) {
        return fetchCustomWindowContext(apiArgs, customWindow);
      }
      return fetchContext(apiArgs);
    },
    staleTime: Infinity,
    keepPreviousData: true,
    initialData: () =>
      allAinB(currentFetchParams, staticData?.staticRecordParams)
        ? staticData?.staticRecords
        : undefined,
  });

  const currentPage = data;
  const tableData = React.useMemo(
    () =>
      currentPage?.records
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
            left_context:
              customWindow === 0
                ? contextRow.left_context.slice(-charLimit)
                : contextRow.left_context,
            pivot: (
              <span className={"text-blue-500 font-medium"}>
                {contextRow.pivot}
              </span>
            ),
            right_context:
              customWindow === 0
                ? contextRow.right_context.slice(0, charLimit)
                : contextRow.right_context,
          }));
        })
        .flat() ?? [],
    [currentPage, charLimit, customWindow]
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

  const pagination = currentPage && (
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
      <p className={"ml-3 md:ml-5 lg:ml-5"}>
        {lang === "fr" ? "de" : "of"} {(cursorMax + 1).toLocaleString()}
      </p>
    </QueryPagination>
  );

  return (
    <div className={" flex flex-col justify-center mb-20"}>
      {tableInstance.data.length > 0 ? (
        <div>
          <div className={"ml-5 flex flex-col mb-2"}>
            {pagination}
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