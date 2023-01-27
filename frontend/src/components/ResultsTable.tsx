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
  const [selectedPapers, setSelectedPapers] = React.useState<
    Paper[] | undefined
  >();

  const { data, isError, isLoading } = trpc.gallicaRecords.useQuery(
    {
      year: props.year,
      month: props.month,
      day: props.day,
      codes: selectedPapers?.map((p) => p.code) || props.codes || [],
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

  return (
    <div className={"flex flex-col"}>
      <div className={"m-auto ml-5 "}>
        <div
          className={
            "flex flex-row flex-wrap gap-5 pt-10 md:gap-10 lg:gap-10"
          }
        >
          {props.children || <></>}
          <InputLabel label={"Periodical"}>
            <PaperDropdown
              onClick={(paper) => {
                if (selectedPapers) {
                  setSelectedPapers([...selectedPapers, paper]);
                } else {
                  setSelectedPapers([paper]);
                }
              }}
            />
          </InputLabel>
        </div>
        <div className={"mb-10 flex flex-row flex-wrap gap-10"}>
          {selectedPapers?.map((paper) => (
            <button
              onClick={() => {
                if (selectedPapers) {
                  setSelectedPapers(
                    selectedPapers.filter((p) => p.code !== paper.code)
                  );
                }
              }}
              key={paper.code}
              className={"border p-5 hover:bg-zinc-100"}
            >
              {paper.title}
            </button>
          ))}
        </div>
      </div>
      <div className="bg-zinc-100">
        <div>
          <div className={"m-4 flex flex-col gap-5"}>
            {data?.map((record, index) => (
              <div
                key={record.url}
                className={"flex flex-col gap-5 bg-white p-5 shadow-md"}
              >
                <div className={"flex flex-row gap-10 text-lg pb-5 flex-wrap"}>
                  <p>{record.term}</p>
                  <p>{record.date}</p>
                  <p>{record.paper_title}</p>
                  <a
                    className={"underline truncate"}
                    href={record.url}
                    target={"_blank"}
                    rel={"noreferrer"}
                  >
                    {record.url}
                  </a>
                </div>
                <Context url={record.url} term={record.term} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
