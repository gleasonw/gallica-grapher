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
        <div className="m-10 mb-20 flex flex-col gap-10 text-left">
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
          <PaperSelector
            papers={papers}
            onPaperClick={(paper) => {
              setPapers(papers.filter((p) => p !== paper));
            }}
            onPaperAdd={(paper) => {
              setPapers([...papers, paper]);
            }}
            from={yearRange[0]}
            to={yearRange[1]}
            smallText={true}
          />
          <RangeInput
            min={1800}
            max={2020}
            value={yearRange}
            onChange={onSliderChange}
          />
        </div>
        <TicketRow tickets={tickets} onGraphedTicketCardClick={onDeleteTicket}>
          <TicketCard onClick={() => handleSubmit()} />
        </TicketRow>
      </div>
    );
  }
};

interface TicketProps {
  ticket?: Ticket;
  onClick: (ticket?: Ticket) => void;
  color?: string;
}

const TicketCard: React.FC<TicketProps> = ({ ticket, onClick, color }) => {
  return (
    <button
      onClick={() => onClick(ticket)}
      className={
        "text-xl transition duration-150 hover:bg-zinc-500 hover:ease-in"
      }
    >
      {ticket ? (
        <div
          className={"relative h-full w-full border border-t-0 border-r-0 p-10"}
        >
          <svg
            className={"absolute top-0 left-0"}
            viewBox="0 0 800 800"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect x="0" y="0" width="80" height="80" fill={color} />
          </svg>
          <div className={"absolute top-0 right-3 text-3xl"}>-</div>
          <div>{ticket.terms.join(", ")}</div>
          <div>{ticket.papers?.map((paper) => paper.title).join(", ")}</div>
        </div>
      ) : (
        <div
          className={
            "m-w-full m-h-full flex h-full flex-col justify-center border-b border-l border-r p-20 pt-10 pb-10 text-3xl"
          }
        >
          +
        </div>
      )}
    </button>
  );
};

const TicketRow: React.FC<{
  tickets?: Ticket[];
  children?: React.ReactNode;
  onGraphedTicketCardClick: (ticket?: Ticket) => void;
}> = ({ tickets, children, onGraphedTicketCardClick }) => {
  return (
    <div className={"z-0 flex border-t bg-white"}>
      <div className={"flex overflow-y-hidden overflow-x-scroll"}>
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
