import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Column, TableInstance, useTable } from "react-table";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { GallicaResponse } from "../models/dbStructs";
import { apiURL } from "./apiURL";
import { useContext } from "react";
import { LangContext } from "../pages";

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

export const fetchContext = async (pageParam = 0, props: TableProps) => {
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
  return (await response.json()) as GallicaResponse;
};

const strings = {
  fr: {
    noResults: "Aucun résultat",
    loading_next: "Chargement de la prochaine page...",
    loading_previous: "Chargement de la page précédente...",
    error: "Erreur",
    total_docs: "documents sur Gallica",
    num_docs_page: "Les occurrences dans 5 documents sont affichées",
  },
  en: {
    noResults: "No results",
    loading_next: "Loading next page...",
    loading_previous: "Loading previous page...",
    error: "Error",
    total_docs: "documents on Gallica",
    num_docs_page: "Occurrences in 5 documents are displayed",
  },
};

export function ResultsTable(props: TableProps) {
  const [selectedPage, setSelectedPage] = React.useState(1);
  const limit = props.limit || 10;
  const { lang } = useContext(LangContext);
  const translation = strings[lang];

  const { isFetching, data } = useQuery({
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
      selectedPage,
    ],
    queryFn: () =>
      fetchContext(selectedPage * props.limit, {
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
            col1: (
              <a
                href={contextRow.page_url}
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
        Header: lang === "fr" ? "Contexte gauche" : "Left context",
        accessor: "col3",
      },
      {
        Header: "Pivot",
        accessor: "col4",
      },
      {
        Header: lang === "fr" ? "Contexte droit" : "Right context",
        accessor: "col5",
      },
    ],
    [lang]
  );

  const tableInstance = useTable({ columns, data: tableData });
  const total_results = Number(data?.num_results) ?? 0;
  const cursorMax = Math.floor(total_results / limit);

  return (
    <div className={"mt-5 flex flex-col justify-center mb-20"}>
      <h1 className={"text-2xl flex flex-col gap-2 ml-5"}>
        {!currentPage && !isFetching && <p>No results found</p>}
        {currentPage && (
          <div className={"flex flex-row gap-10"}>
            {total_results.toLocaleString()} {translation.total_docs}
          </div>
        )}
        <p className={"text-xl"}>{translation.num_docs_page}</p>
      </h1>
      <h1
        className={
          "flex flex-row justify-center items-center text-xl md:text-2xl lg:text-2xl"
        }
      >
        {isFetching && <p>{translation.loading_next}</p>}
      </h1>
      {currentPage && !isFetching && (
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
      )}
      {props.children}
      <DesktopTable tableInstance={tableInstance} />
      <MobileTable tableInstance={tableInstance} />
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
        "flex flex-row justify-center items-center text-xl md:text-2xl lg:text-2xl mt-5 mb-5"
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
          <div {...row.getRowProps()} key={index} className={"odd:bg-zinc-100"}>
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
  );
}

function DesktopTable(props: { tableInstance: TableInstance<any> }) {
  return (
    <table className={"shadow-md hidden md:block lg:block"}>
      <thead>
        {props.tableInstance.headerGroups.map((headerGroup, index) => (
          <tr {...headerGroup.getHeaderGroupProps()} key={index}>
            {headerGroup.headers.map((column, index) => (
              <th {...column.getHeaderProps()} key={index}>
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
              key={index}
              className={"odd:bg-zinc-100"}
            >
              {row.cells.map((cell, index) => {
                let twStyle = "";
                if (
                  cell.column.Header === "Left context" ||
                  cell.column.Header === "Contexte gauche"
                ) {
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
  );
}
