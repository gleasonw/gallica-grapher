import React from "react";
import { trpc } from "../utils/trpc";
import { Paper } from "../server/routers/_app";
import { InputLabel } from "./InputLabel";
import { PaperDropdown } from "./PaperDropdown";
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
  const { data, isError, isLoading } = trpc.gallicaRecords.useQuery(
    {
      year: props.year,
      month: props.month,
      day: props.day,
      codes: props.codes || [],
      terms: props.terms || [],
    },
    { staleTime: Infinity, keepPreviousData: true }
  );

  if (isLoading || !data) {
    return <div>Loading...</div>;
  }

  if (isError) {
    return <div>Error</div>;
  }

  const gallicaResponse = data;

  return (
    <div className={"flex flex-col"}>
      <div className={"m-auto ml-5 "}>{props.children}</div>
      <div className="bg-zinc-100">
        <div>
          <div className={"m-4 flex flex-col gap-5"}>
            <h1 className={'text-2xl'}>{gallicaResponse.num_records_in_gallica.toLocaleString()} records</h1>
            {gallicaResponse?.records.map((record, index) => (
              <div
                key={record.url}
                className={"flex flex-col gap-5 bg-white p-5 shadow-md"}
              >
                <div className={"flex flex-row flex-wrap gap-10 pb-5 text-lg"}>
                  <p>{record.term}</p>
                  <p>{record.date}</p>
                  <p >{record.paper_title}</p>
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
