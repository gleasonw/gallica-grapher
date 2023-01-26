import React from "react";
import { trpc } from "../utils/trpc";
import { Ticket } from "../pages/index";
import { GallicaRecord, Paper } from "../server/routers/_app";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { ContextCell } from "./ContextCell";
import { PaperDropdown } from "./PaperDropdown";

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
            "gap-5 flex flex-row flex-wrap pt-10 pb-10 md:gap-10 lg:gap-10"
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
        <div className={"flex flex-row mb-10 flex-wrap gap-10"}>
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
              className={"p-5 border hover:bg-zinc-100"}
            >
              {paper.title}
            </button>
          ))}
        </div>
      </div>
      <div className="bg-zinc-100">
        <div className={"hidden md:block lg:block"}>
          <LargeTable data={data} />
        </div>
        <div className={"md:hidden lg:hidden"}>
          <MobileTable data={data} />
        </div>
      </div>
    </div>
  );
};

export const LargeTable: React.FC<{ data: GallicaRecord[] }> = ({ data }) => {
  return (
    <table className={"table-auto w-full h-full"}>
      <thead>
        <tr>
          <th>Term</th>
          <th>Date</th>
          <th>Periodical</th>
          <th>Text Image on Gallica</th>
          <th>Context</th>
        </tr>
      </thead>
      <tbody>
        {data?.map((record, index) => (
          <tr key={index} className={"odd:bg-white"}>
            <Cell>{record.term}</Cell>
            <Cell>{record.date}</Cell>
            <Cell>{record.paper_title}</Cell>
            <Cell>
              <a
                href={record.url}
                className={"underline"}
                target={"_blank"}
                rel={"noreferrer"}
              >
                Full text image
              </a>
            </Cell>
            <ContextCell record={record} />
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export const MobileTable: React.FC<{ data: GallicaRecord[] }> = ({ data }) => {
  return (
    <table className={"table-auto w-full h-full"}>
      <thead>
        <tr className={"table-row"}>
          <th>Term</th>
          <th>Date</th>
          <th>Context</th>
        </tr>
      </thead>
      <tbody>
        {data?.map((record, index) => (
          <tr key={index} className={"odd:bg-white"}>
            <td>{record.term}</td>
            <td>{record.date}</td>
            <ContextCell record={record} />
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export const Cell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <td className={"p-5"}>{children}</td>;
};
