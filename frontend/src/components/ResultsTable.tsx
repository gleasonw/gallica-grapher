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
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { GallicaResponse } from "../models/dbStructs";
import { useContext } from "react";
import { LangContext } from "./LangContext";

export interface TableProps {
  terms?: string[];
  codes?: string[];
  day?: number | null;
  month?: number | null;
  yearRange?: [number | undefined, number | undefined];
  source?: "book" | "periodical" | "all" | null;
  link_term?: string | null;
  link_distance?: number | null;
  children?: React.ReactNode;
  limit: number;
  sort?: "date" | "relevance" | null;
  initialRecords?: Awaited<ReturnType<typeof fetchContext>>;
}

export const fetchContext = async (pageParam = 0, props: TableProps) => {
  let baseUrl = `https://gallica-grapher.ew.r.appspot.com/api/gallicaRecords`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...props,
    children: undefined,
    initialRecords: undefined,
    cursor: pageParam,
    limit: props.limit,
    row_split: true,
    all_context: true,
    year: props.yearRange?.[0],
    end_year: props.yearRange?.[1],
    yearRange: undefined,
  });
  console.log(url);
  const response = await fetch(url);
  return (await response.json()) as GallicaResponse;
};

export function ResultsTable(props: TableProps) {
  const [selectedPage, setSelectedPage] = React.useState(1);
  const [charLimit, setCharLimit] = React.useState(70);
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
  const translation = strings[lang];

  const { isFetching, data } = useQuery({
    queryKey: [
      "context",
      props.yearRange,
      props.month,
      props.day,
      props.codes,
      props.terms,
      props.source,
      props.link_term,
      props.link_distance,
      props.limit,
      props.sort,
      selectedPage,
    ],
    queryFn: () =>
      fetchContext((selectedPage - 1) * props.limit, {
        ...props,
        children: undefined,
      }),
    staleTime: Infinity,
    keepPreviousData: true,
    placeholderData: props.initialRecords,
  });

  const currentPage = data;
  const tableData = React.useMemo(
    () =>
      currentPage?.records
        ?.map((record) =>
          record.context.map((contextRow) => ({
            document: `${record.paper_title}||${record.date}`,
            date: record.date,
            page: (
              <a
                className="underline font-medium p-2"
                href={contextRow.page_url}
                target="_blank"
                rel="noreferrer"
              >
                Image
              </a>
            ),
            left_context: contextRow.left_context.slice(-charLimit),
            pivot: (
              <span className={"text-blue-500 font-medium"}>
                {contextRow.pivot}
              </span>
            ),
            right_context: contextRow.right_context.slice(0, charLimit),
          }))
        )
        .flat() ?? [],
    [currentPage, charLimit]
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
            {value.split("||").map((v, i) =>
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

  const pagination = currentPage && !isFetching && (
    <QueryPagination
      onPageIncrement={() => setSelectedPage(selectedPage + 1)}
      onPageDecrement={() => setSelectedPage(selectedPage - 1)}
      selectedPage={selectedPage}
      cursorMax={cursorMax}
      onLastPage={() => setSelectedPage(cursorMax)}
      onFirstPage={() => setSelectedPage(1)}
    >
      <p className={"mr-3 md:mr-5 lg:mr-5"}>Page</p>
      <CursorInput
        cursor={selectedPage}
        cursorMax={cursorMax}
        onCursorIncrement={setSelectedPage}
        onCursorDecrement={setSelectedPage}
      />
      <p className={"ml-3 md:ml-5 lg:ml-5"}>
        {lang === "fr" ? "de" : "of"} {cursorMax.toLocaleString()}
      </p>
    </QueryPagination>
  );

  const spinner = isFetching && (
    <div className={"flex justify-center items-center"}>
      <div
        className=" h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"
        role="status"
      />
    </div>
  );
  //TODO: show active filters, replicate gamepass ui
  return (
    <div className={"mt-5 flex flex-col justify-center mb-20"}>
      <div className={"ml-5 flex flex-col mb-2"}>
        <h1 className={"text-2xl flex flex-col gap-2"}>
          {!currentPage && !isFetching && <p>No results found</p>}
          {currentPage && (
            <div className={"flex flex-row gap-10"}>
              {total_results.toLocaleString()} {translation.total_docs}
            </div>
          )}
        </h1>
        {spinner}
        {pagination}
      </div>
      {tableInstance.data.length > 0 && (
        <div
          className={
            "flex ease-in-out first-letter:flex-col justify-center items-center transition-all duration-1000"
          }
        >
          <DesktopTable tableInstance={tableInstance} />
          <MobileTable tableInstance={tableInstance} />
        </div>
      )}
      {pagination}
    </div>
  );
}

function QueryPagination(props: {
  children: React.ReactNode;
  selectedPage: number;
  cursorMax: number;
  onFirstPage: () => void;
  onPageIncrement: () => void;
  onPageDecrement: () => void;
  onLastPage: () => void;
}) {
  return (
    <div
      className={
        "flex flex-row justify-center items-center text-xl md:text-2xl lg:text-2xl transition-all duration-300"
      }
    >
      {props.selectedPage !== 1 && (
        <div className={"flex flex-row justify-between"}>
          <button onClick={props.onFirstPage} className={"p-3"}>
            {"<<"}
          </button>
          <button className={"p-4"} onClick={props.onPageDecrement}>
            {"<"}
          </button>
        </div>
      )}
      {props.children}
      {props.selectedPage !== props.cursorMax && (
        <div className={"flex flex-row justify-between"}>
          <button className={"p-4"} onClick={props.onPageIncrement}>
            {">"}
          </button>
          <button onClick={props.onLastPage} className={"p-3"}>
            {">>"}
          </button>
        </div>
      )}
    </div>
  );
}

interface CursorInputProps {
  cursor: number;
  cursorMax: number;
  onCursorIncrement: (amount: number) => void;
  onCursorDecrement: (amount: number) => void;
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
        "shadow-xl rounded-xl border hidden md:block lg:block xl:block transition-all duration-300"
      }
    >
      <thead>
        {props.tableInstance.headerGroups.map((headerGroup, index) => (
          <tr {...headerGroup.getHeaderGroupProps()} key={index}>
            {headerGroup.headers.map((column, index) => (
              <th
                {...column.getHeaderProps()}
                key={index}
                className={"p-2 font-medium"}
              >
                {column.render("Header")}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...props.tableInstance.getTableBodyProps()}>
        {props.tableInstance.rows.map((row, index) => {
          props.tableInstance.prepareRow(row);
          return (
            <tr
              {...row.getRowProps()}
              className={"odd:bg-zinc-100"}
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
                    className={"pl-6 pr-6 pt-2 pb-2" + twStyle}
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
