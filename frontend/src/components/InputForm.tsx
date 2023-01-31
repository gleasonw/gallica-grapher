import React, { useState } from "react";
import { Ticket } from "../pages/index";
import { TextInput } from "./TextInput";
import { PaperSelector } from "./PaperSelector";
import { RangeInput } from "./RangeInput";
import { SearchProgress } from "./SearchProgress";
import { seriesColors } from "./ResultViewer";
import { useMutation } from "@tanstack/react-query";
import { Paper } from "../models/dbStructs";
import { apiURL } from "./apiURL";

export interface InputFormProps {
  onCreateTicket: (ticket: Ticket) => void;
  onDeleteTicket: (ticket?: Ticket) => void;
  tickets?: Ticket[];
  onSliderChange: (value: [number, number]) => void;
  yearRange: [number, number];
}

export const InputForm: React.FC<InputFormProps> = ({
  onCreateTicket,
  onDeleteTicket,
  onSliderChange,
  yearRange,
  tickets,
}) => {
  const [word, setWord] = useState<string>("");
  const [papers, setPapers] = useState<Paper[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const [ticketID, setTicketID] = useState<number>(0);

  async function postTicket(ticket: Ticket): Promise<{ requestid: number }> {
    const response = await fetch(`${apiURL}/api/init`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(ticket),
    });
    const data = await response.json();
    return data as { requestid: number };
  }

  const mutation = useMutation(postTicket);

  const handleSubmit = () => {
    mutation.mutateAsync(
      {
        terms: [word],
        papers: papers,
        start_date: yearRange[0],
        end_date: yearRange[1],
        grouping: "month",
        id: ticketID,
      },
      {
        onSuccess: (data) => {
          setTicketID(data.requestid);
          setSubmitted(true);
          //remove example ticket
          onDeleteTicket(tickets?.find((ticket) => ticket.example));
        },
      }
    );
  };

  if (submitted) {
    return (
      <div>
        <SearchProgress
          ticket={{
            id: ticketID,
            terms: [word],
            papers: papers,
            start_date: yearRange[0],
            end_date: yearRange[1],
            grouping: "month",
          }}
          onFetchComplete={(backendSource: "gallica" | "pyllica") => {
            onCreateTicket({
              id: ticketID,
              backend_source: backendSource,
              terms: [word],
              papers: papers,
              start_date: yearRange[0],
              end_date: yearRange[1],
              grouping: "month",
            });
            setSubmitted(false);
            setWord("");
          }}
          onNoRecordsFound={() => {
            alert("No records found for this search");
            setSubmitted(false);
            setWord("");
          }}
        />
        <TicketRow
          tickets={tickets}
          onGraphedTicketCardClick={onDeleteTicket}
        />
      </div>
    );
  } else {
    return (
      <div>
        <div className="m-10 flex flex-col gap-10 text-left">
          <TextInput
            placeholder={"Search term"}
            value={word}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setWord(e.target.value)
            }
            onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
              if (e.key === "Enter") {
                handleSubmit();
              }
            }}
          />
          <RangeInput
            min={1800}
            max={2020}
            value={yearRange}
            onChange={onSliderChange}
          />
          <TicketRow
            tickets={tickets}
            onGraphedTicketCardClick={onDeleteTicket}
          />
        </div>
      </div>
    );
  }
};

interface TicketProps {
  ticket: Ticket;
  onClick: (ticket?: Ticket) => void;
  color?: string;
}

const TicketCard: React.FC<TicketProps> = ({ ticket, onClick, color }) => {
  return (
    <button
      onClick={() => onClick(ticket)}
      className={
        "bg-white text-xl transition duration-150 hover:bg-zinc-500 hover:ease-in"
      }
    >
      <div
        className={"border-rounded relative h-full w-full border p-5 shadow-md"}
      >
        <div className={"absolute top-0 right-3 text-3xl"}>-</div>
        <div>{ticket.terms.join(", ")}</div>
        <div>{ticket.papers?.map((paper) => paper.title).join(", ")}</div>
      </div>
    </button>
  );
};

const TicketRow: React.FC<{
  tickets?: Ticket[];
  children?: React.ReactNode;
  onGraphedTicketCardClick: (ticket?: Ticket) => void;
}> = ({ tickets, children, onGraphedTicketCardClick }) => {
  return (
    <div className={"z-0 flex"}>
      <div className={"flex flex-wrap gap-10"}>
        {tickets?.map((ticket, index) => (
          <TicketCard
            key={ticket.id}
            ticket={ticket}
            onClick={(ticket) => onGraphedTicketCardClick(ticket)}
            color={seriesColors[index % seriesColors.length]}
          />
        ))}
      </div>
      {children}
    </div>
  );
};
