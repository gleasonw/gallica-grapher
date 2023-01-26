import React, { useState } from "react";
import { Paper } from "../server/routers/_app";
import { trpc } from "../utils/trpc";
import { Ticket } from "../pages/index";
import { TextInput } from "./TextInput";
import { PaperSelector as PaperInput } from "./PaperSelector";
import { RangeInput } from "./RangeInput";
import { SearchProgress } from "./SearchProgress";
import { seriesColors } from "./ResultViewer";

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
  const mutation = trpc.search.useMutation();

  const handleSubmit = () => {
    mutation.mutateAsync(
      {
        terms: [word],
        codes: papers.map((p) => p.code),
        start_date: yearRange[0],
        end_date: yearRange[1],
        grouping: "month",
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
            alert("No records found for this search")
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
        <div className="flex flex-col gap-10 text-left m-10 mb-20">
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
          <PaperInput
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
        "text-xl hover:bg-zinc-500 transition duration-150 hover:ease-in"
      }
    >
      {ticket ? (
        <div
          className={"border border-t-0 border-r-0 p-10 w-full h-full relative"}
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
            "border-b border-l border-r h-full p-20 pt-10 pb-10 m-w-full m-h-full text-3xl justify-center flex flex-col"
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
    <div className={"flex border-t z-0 bg-white"}>
      <div className={"flex overflow-x-scroll overflow-y-hidden"}>
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
