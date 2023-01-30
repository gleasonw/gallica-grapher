import React from "react";
import { Ticket } from "../pages/index";
import { ResultsTable, TableProps } from "./ResultsTable";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { Paper } from "../server/routers/_app";
import { PaperDropdown } from "./PaperDropdown";

export interface TicketTableProps extends TableProps {
  onSelectMonth: (month: number) => void;
  onSelectYear: (year: number) => void;
  onSelectDay: (day: number) => void;
  tickets: Ticket[];
}

export const TicketResultTable: React.FC<TicketTableProps> = (props) => {
  const [selectedTicket, setSelectedTicket] = React.useState<Ticket>();
  const [selectedPapers, setSelectedPapers] = React.useState<
    Paper[] | undefined
  >();
  let tableTerms: string[] = [];
  let tableCodes: string[] = [];
  if (selectedTicket) {
    tableTerms = selectedTicket.terms;
    if (selectedTicket.papers) {
      tableCodes = selectedTicket.papers.map((p) => p.code);
    }
  } else if (props.tickets && props.tickets.length > 0) {
    tableTerms = props.tickets[0].terms;
    if (props.tickets[0].papers) {
      tableCodes = props.tickets[0].papers.map((p) => p.code);
    }
  }

  return (
    <ResultsTable
      terms={tableTerms}
      codes={tableCodes || selectedPapers?.map((p) => p.code) || []}
      month={props.month}
      day={props.day}
      year={props.year}
    >
      <div
        className={"flex flex-row flex-wrap gap-5 pt-10 md:gap-10 lg:gap-10"}
      >
        <InputLabel label={"Year"}>
          <input
            type={"number"}
            className={"border  bg-white p-5"}
            value={props.year}
            onChange={(e) => props.onSelectYear(parseInt(e.target.value))}
          />
        </InputLabel>
        <InputLabel label={"Month"}>
          <SelectInput
            options={Array.from(Array(12).keys()).map((i) => String(i))}
            onChange={(value) => props.onSelectMonth(parseInt(value))}
            value={props.month ? String(props.month) : undefined}
          />
        </InputLabel>
        <InputLabel label={"Day"}>
          <SelectInput
            options={Array.from(Array(31).keys()).map((i) => String(i))}
            onChange={(value) => props.onSelectDay(parseInt(value))}
            value={props.day ? String(props.day) : undefined}
          />
        </InputLabel>
        <InputLabel label={"Ticket"}>
          <select
            onChange={(e) => {
              if (!props.tickets) {
                return;
              }
              setSelectedTicket(
                props.tickets.find(
                  (t) => t.id === parseInt(e.target.value)
                ) as Ticket
              );
            }}
            className={"border  bg-white p-5"}
          >
            {props.tickets?.map((ticket) => (
              <option key={ticket.id} value={ticket.id}>
                {ticket.terms}
              </option>
            ))}
          </select>
        </InputLabel>
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
    </ResultsTable>
  );
};
