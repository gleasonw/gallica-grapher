import React, { useState } from "react";
import { GraphTicket } from "./GraphTicket";
import Image from "next/image";
import glassIcon from "./assets/glass.svg";
import { SearchProgress } from "./SearchProgress";
import { seriesColors } from "./utils/makeHighcharts";
import { useMutation } from "@tanstack/react-query";
import { apiURL } from "./apiURL";
import { useContext } from "react";
import { LangContext } from "./LangContext";
import InputBubble from "./InputBubble";
import DashboardLayout from "./DashboardLayout";
import { YearRangeInput } from "../pages";
import {
  GraphPageDispatchContext,
  GraphPageStateContext,
} from "./GraphContext";

export interface InputFormProps {
  onCreateTicket: (ticket: GraphTicket) => void;
  onDeleteTicket: (ticketID: number) => void;
  onDeleteExampleTickets: () => void;
  tickets?: GraphTicket[];
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
  tickets,
}) => {
  const [word, setWord] = useState<string>("");
  const [submitted, setSubmitted] = useState(false);
  const [ticketID, setTicketID] = useState<number>(0);
  const graphStateDispatch = React.useContext(GraphPageDispatchContext);
  const graphState = React.useContext(GraphPageStateContext);
  if (!graphStateDispatch || !graphState)
    throw new Error("No graph state dispatch found");
  const { lang } = useContext(LangContext);
  const translation = strings[lang];
  const { searchYearRange } = graphState;

  function setSearchRange(newRange: [number | undefined, number | undefined]) {
    console.log(newRange);
    graphStateDispatch!({
      type: "set_search_range",
      payload: newRange,
    });
  }

  async function postTicket(
    ticket: GraphTicket
  ): Promise<{ requestid: number }> {
    console.log(ticket);
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
    setSubmitted(true);
    mutation.mutateAsync(
      {
        terms: [word],
        start_date: searchYearRange[0],
        end_date: searchYearRange[1],
        grouping: "month",
        id: ticketID,
      },
      {
        onSuccess: (data) => {
          setTicketID(data.requestid);
        },
      }
    );
  };

  return (
    <DashboardLayout>
      <div
        className={
          "w-full flex flex-col justify-center items-center rounded-full"
        }
      >
        <InputBubble
          word={word}
          onWordChange={submitted ? () => undefined : setWord}
          onSubmit={handleSubmit}
        >
          <Image
            src={glassIcon}
            className={"w-8 h-8 absolute top-5 right-5 hover:cursor-pointer"}
            alt="Search icon"
            onClick={handleSubmit}
          />
        </InputBubble>
        <YearRangeInput
          max={2021}
          min={1500}
          value={searchYearRange}
          showLabel={false}
          onChange={setSearchRange}
        />
      </div>
      {submitted && (
        <SearchProgress
          ticket={{
            id: ticketID,
            terms: [word],
            start_date: searchYearRange[0],
            end_date: searchYearRange[1],
            grouping: "month",
          }}
          onFetchComplete={(backendSource: "gallica" | "pyllica") => {
            onCreateTicket({
              id: ticketID,
              backend_source: backendSource,
              terms: [word],
              start_date: searchYearRange[0],
              end_date: searchYearRange[1],
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
      <TicketRow
        tickets={tickets}
        onGraphedTicketCardClick={onDeleteTicket}
        submitted={submitted}
      />
    </DashboardLayout>
  );
};

export const TicketRow: React.FC<{
  tickets?: GraphTicket[];
  children?: React.ReactNode;
  onGraphedTicketCardClick: (ticketID: number) => void;
  submitted: boolean;
}> = ({ tickets, children, onGraphedTicketCardClick, submitted }) => {
  return (
    <div className={"z-0 flex self-start"}>
      <div className={"flex flex-wrap gap-10"}>
        {tickets?.map((ticket, index) => (
          <TicketCard
            key={ticket.id}
            ticket={ticket}
            onClick={onGraphedTicketCardClick}
            color={seriesColors[index % seriesColors.length]}
          />
        ))}
        {submitted && (
          <div
            className={"rounded-lg border-2 bg-white p-3 text-xl shadow-md"}
            style={{
              borderColor:
                seriesColors[tickets?.length || 0 % seriesColors.length],
            }}
          >
            <div className="flex items-center justify-center mt-2">
              <div
                className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"
                role="status"
              >
                <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">
                  Loading...
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
      {children}
    </div>
  );
};

interface TicketProps {
  ticket: GraphTicket;
  onClick: (ticketID: number) => void;
  color?: string;
}

const TicketCard: React.FC<TicketProps> = ({ ticket, onClick, color }) => {
  return (
    <button
      onClick={() => onClick(ticket.id)}
      className={`rounded-lg border-2 bg-white p-3 text-xl shadow-md transition duration-150 hover:bg-zinc-500 hover:ease-in`}
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
