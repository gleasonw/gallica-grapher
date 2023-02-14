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
  onSelectTicket: (ticket: Ticket) => void;
  selectedTicket: Ticket | null;
  tickets: Ticket[];
  initialRecords: Awaited<ReturnType<typeof fetchContext>>;
}

export const TicketResultTable: React.FC<TicketTableProps> = (props) => {
  const [selectedPapers, setSelectedPapers] = React.useState<
    Paper[] | undefined
  >();
  const [formDisplayLinkTerm, setFormDisplayLinkTerm] = React.useState<
    string | null
  >();
  const [passedLinkTerm, setPassedLinkTerm] = React.useState<string | null>();
  const [selectedDistance, setSelectedDistance] = React.useState<number | null>(
    10
  );
  const [typingTimeout, setTypingTimeout] =
    React.useState<NodeJS.Timeout | null>(null);

  function handleLinkChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFormDisplayLinkTerm(e.target.value);
    if (typingTimeout) {
      clearTimeout(typingTimeout);
    }
    setTypingTimeout(
      setTimeout(() => {
        setPassedLinkTerm(e.target.value);
      }, 500)
    );
  }

  React.useEffect(() => {
    setFormDisplayLinkTerm(null);
    setPassedLinkTerm(null);
  }, [props.month, props.day, props.year, props.selectedTicket]);

  const tableKey = [
    props.month,
    props.day,
    props.year,
    props.selectedTicket?.id,
    passedLinkTerm,
    selectedDistance,
    selectedPapers
  ]

  return (
    <ResultsTable
      terms={props.selectedTicket?.terms}
      codes={selectedPapers?.map((p) => p.code) || []}
      month={props.month}
      day={props.day}
      year={props.year}
      limit={5}
      link_term={passedLinkTerm}
      link_distance={selectedDistance}
      initialRecords={props.initialRecords}
      source={"periodical"}
      key={tableKey.join("-")}
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
        <InputLabel label={"Link search"}>
          <div className={"align-center flex flex-row justify-center"}>
            <input
              className={"relative max-w-full border p-5"}
              value={formDisplayLinkTerm || ""}
              onChange={handleLinkChange}
            />
            <p className={"p-5"}>within</p>
            <input
              className={"relative w-20 border p-5"}
              value={selectedDistance || ""}
              onChange={(e) => setSelectedDistance(parseInt(e.target.value))}
            />
            <p className={"p-5"}>words</p>
          </div>
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
