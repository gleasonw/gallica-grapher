import React, { useContext } from "react";
import { LangContext } from "../pages";
import { Ticket } from "../pages/index";
import { ResultsTable, TableProps, fetchContext } from "./ResultsTable";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { PaperDropdown } from "./PaperDropdown";
import { Paper } from "../models/dbStructs";

export interface TicketTableProps extends TableProps {
  onSelectMonth: (month: number | null) => void;
  onSelectYear: (year: number | null) => void;
  onSelectTicket: (ticketID: number) => void;
  selectedTicket: number | null;
  tickets?: Ticket[];
  initialRecords: Awaited<ReturnType<typeof fetchContext>>;
}

export const TicketResultTable: React.FC<TicketTableProps> = (props) => {
  const [selectedPapers, setSelectedPapers] = React.useState<
    Paper[] | undefined
  >();

  const tableKey = [
    props.month,
    props.day,
    props.year,
    props.selectedTicket,
    selectedPapers,
  ];
  const { lang } = useContext(LangContext);

  return (
    <ResultsTable
      terms={
        (props.tickets &&
          props.tickets.length > 0 &&
          props.tickets.filter((t) => t.id === props.selectedTicket)[0]
            .terms) ||
        []
      }
      codes={selectedPapers?.map((p) => p.code) || []}
      month={props.month}
      day={props.day}
      year={props.year}
      limit={10}
      initialRecords={props.initialRecords}
      source={"periodical"}
      key={tableKey.join("-")}
    >
      <div className={"flex flex-row flex-wrap gap-5 md:gap-10 lg:gap-10"}>
        <InputLabel label={lang === "fr" ? "Année" : "Year"}>
          <input
            type={"number"}
            className={"border  bg-white p-5"}
            value={props.year || ""}
            onChange={(e) => props.onSelectYear(parseInt(e.target.value))}
          />
        </InputLabel>
        <InputLabel label={lang === "fr" ? "Mois" : "Month"}>
          <SelectInput
            options={Array.from(Array(12).keys()).map((i) => String(i))}
            onChange={(value) => props.onSelectMonth(parseInt(value))}
            value={props.month ? String(props.month) : undefined}
          />
        </InputLabel>
        <InputLabel label={"Ticket"}>
          <select
            onChange={(e) => {
              props.onSelectTicket(parseInt(e.target.value));
            }}
            className={"border  bg-white p-5"}
            value={props.selectedTicket || ""}
          >
            {props.tickets?.map((ticket) => (
              <option key={ticket.id} value={ticket.id}>
                {ticket.terms}
              </option>
            ))}
          </select>
        </InputLabel>
        <InputLabel label={lang === "fr" ? "Périodique" : "Periodical"}>
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
      <div className={"mt-5 flex flex-row flex-wrap gap-10"}>
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
