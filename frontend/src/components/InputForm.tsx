import React, { useState } from "react";
import { Ticket } from "../pages/index";
import Image from "next/image";
import glassIcon from "./assets/glass.svg";
import { SearchProgress } from "./SearchProgress";
import { seriesColors } from "./ResultViewer";
import { useMutation } from "@tanstack/react-query";
import { apiURL } from "./apiURL";
import { useContext } from "react";
import { LangContext } from "../pages/index";

export interface InputFormProps {
  onCreateTicket: (ticket: Ticket) => void;
  onDeleteTicket: (ticket?: Ticket) => void;
  onDeleteExampleTickets: () => void;
  tickets?: Ticket[];
  onSliderChange: (value: [number, number]) => void;
  yearRange: [number, number];
}

const strings = {
  fr: {
    no_records_found: "Aucun résultat trouvé",
    search_for_word: "Rechercher un mot",
  },
  en: {
    no_records_found: "No records found",
    search_for_word: "Search for a word",
  },
};

export const InputForm: React.FC<InputFormProps> = ({
  onCreateTicket,
  onDeleteTicket,
  yearRange,
  tickets,
}) => {
  const [word, setWord] = useState<string>("");
  const [submitted, setSubmitted] = useState(false);
  const [ticketID, setTicketID] = useState<number>(0);
  const { lang } = useContext(LangContext);
  const translation = strings[lang];

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

  return (
    <div className="ml-10 mr-10 mb-10 flex flex-col gap-10">
      <div className="justify-center items-center flex flex-col mt-10">
        <div className="text-2xl relative w-full max-w-3xl">
          <input
            className={"p-5 w-full rounded-3xl border-2 hover:shadow-lg"}
            placeholder={translation.search_for_word}
            value={word || ""}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setWord(e.target.value)
            }
            onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => {
              if (e.key === "Enter") {
                handleSubmit();
              }
            }}
          />
          <Image
            src={glassIcon}
            className={"w-8 h-8 absolute top-5 right-5 hover:cursor-pointer"}
            alt="Search icon"
            onClick={() => handleSubmit()}
          />
        </div>
        {!submitted && <div className={"mt-10"}></div>}
        {submitted && (
          <SearchProgress
            ticket={{
              id: ticketID,
              terms: [word],
              start_date: yearRange[0],
              end_date: yearRange[1],
              grouping: "month",
            }}
            onFetchComplete={(backendSource: "gallica" | "pyllica") => {
              onCreateTicket({
                id: ticketID,
                backend_source: backendSource,
                terms: [word],
                start_date: yearRange[0],
                end_date: yearRange[1],
                grouping: "month",
              });
              setSubmitted(false);
              setWord("");
            }}
            onNoRecordsFound={() => {
              alert(translation.no_records_found);
              setSubmitted(false);
              setWord("");
            }}
          />
        )}
      </div>
      <TicketRow tickets={tickets} onGraphedTicketCardClick={onDeleteTicket} />
    </div>
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

interface TicketProps {
  ticket: Ticket;
  onClick: (ticket?: Ticket) => void;
  color?: string;
}

const TicketCard: React.FC<TicketProps> = ({ ticket, onClick, color }) => {
  return (
    <button
      onClick={() => onClick(ticket)}
      className={`rounded-lg border-2 bg-white p-5 text-xl shadow-md transition duration-150 hover:bg-zinc-500 hover:ease-in`}
      style={{ borderColor: color }}
    >
      <div className={`relative h-full w-full`}>
        <div className={"flex flex-row gap-10"}>
          <p>{ticket.terms.join(", ")}</p>
          <p className={"text-zinc-600"}>x</p>
        </div>
        <div>{ticket.papers?.map((paper) => paper.title).join(", ")}</div>
      </div>
    </button>
  );
};
