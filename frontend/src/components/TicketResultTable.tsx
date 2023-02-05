import React from "react";
import { Ticket } from "../pages/index";
import { ResultsTable, TableProps, fetchContext } from "./ResultsTable";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { PaperDropdown } from "./PaperDropdown";
import { Paper } from "../models/dbStructs";

export interface TicketTableProps extends TableProps {
  onSelectMonth: (month: number | null) => void;
  onSelectYear: (year: number | null) => void;
  onSelectDay: (day: number | null) => void;
  onSelectTicket: (ticket: Ticket) => void;
  selectedTicket: Ticket | null;
  tickets: Ticket[];
  initialRecords: Awaited<ReturnType<typeof fetchContext>>;
}

export const TicketResultTable: React.FC<TicketTableProps> = (props) => {
  const [selectedPapers, setSelectedPapers] = React.useState<
    Paper[] | undefined
  >();



  return (
    <ResultsTable
      terms={props.selectedTicket?.terms}
      codes={selectedPapers?.map((p) => p.code) || []}
      month={props.month}
      day={props.day}
      year={props.year}
      limit={10}
      initialRecords={props.initialRecords}
      source={"periodical"}
    >
      <div
        className={"flex flex-row flex-wrap gap-5 pt-10 md:gap-10 lg:gap-10"}
      >
        <InputLabel label={"Year"}>
          <input
            type={"number"}
            className={"border  bg-white p-5"}
            value={props.year || ""}
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
              props.onSelectTicket(
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
