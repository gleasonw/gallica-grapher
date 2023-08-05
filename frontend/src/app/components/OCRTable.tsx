"use client";

import { fetchContext } from "./fetchContext";
import {
  Cell,
  Row,
  TableInstance,
  useExpanded,
  useGroupBy,
  useTable,
} from "react-table";
import React, { Suspense } from "react";
import { ImageSnippet } from "./ImageSnippet";

export function OCRTable({
  data,
  children,
}: {
  data: Awaited<ReturnType<typeof fetchContext>>;
  children: React.ReactNode[];
}) {
  const lang = "fr";

  const tableData = React.useMemo(
    () =>
      data?.records
        ?.map((record, recordIndex) => {
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
          return record.context.map((contextRow, index) => ({
            ...documentMeta,
            page: (
              <div className={"flex"}>
                <a
                  className="underline font-medium p-2"
                  href={contextRow.page_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {index === 0 && children?.[recordIndex]}
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
    [data, children]
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
  const cursorMax = Math.floor(total_results / 10);

  return (
    <div className={" flex flex-col justify-center mb-20"}>
      {tableInstance.data.length > 0 && (
        <div>
          <div>
            <DesktopTable tableInstance={tableInstance} />
            <MobileTable tableInstance={tableInstance} />
          </div>
        </div>
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
