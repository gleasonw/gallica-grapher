import React, { useState } from "react";
import { GraphTicket } from "./GraphTicket";
import Image from "next/image";
import link from "./assets/link.svg";
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
import { SubInputLayout } from "./SubInputLayout";
import { SelectInput } from "./SelectInput";

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
  onDeleteExampleTickets,
}) => {
  const [word, setWord] = useState<string>("");
  const [submitted, setSubmitted] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [ticketID, setTicketID] = useState<number>(0);
  const graphStateDispatch = React.useContext(GraphPageDispatchContext);
  const graphState = React.useContext(GraphPageStateContext);
  if (!graphStateDispatch || !graphState)
    throw new Error("No graph state dispatch found");
  const { lang } = useContext(LangContext);
  const translation = strings[lang];
  const { searchYearRange, source, linkTerm } = graphState;

  function setSearchRange(newRange: [number | undefined, number | undefined]) {
    graphStateDispatch!({
      type: "set_search_range",
      payload: newRange,
    });
  }

  async function postTicket(
    ticket: GraphTicket
  ): Promise<{ requestid: number }> {
    const response = await fetch(`${apiURL}/api/init`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({...ticket, link_term: ticket.linkTerm}),
    });
    const data = await response.json();
    return data as { requestid: number };
  }

  const mutation = useMutation(postTicket);
  const currentTicket: GraphTicket = {
    terms: [word],
    start_date: searchYearRange[0],
    end_date: searchYearRange[1],
    id: ticketID,
    source,
    linkTerm,
  };

  const reset = () => {
    setFetching(false);
    setSubmitted(false);
    setWord("");
  };

  const handleSubmit = () => {
    if (!word) return;
    setSubmitted(true);
    onDeleteExampleTickets();
    mutation.mutateAsync(currentTicket, {
      onSuccess: (data) => {
        setTicketID(data.requestid);
        setFetching(true);
      },
    });
  };

  const corpusOptions: GraphTicket["source"][] = [
    "presse",
    "livres",
  ];

  return (
    <DashboardLayout>
      <div
        className={
          "w-full flex flex-col justify-center items-center rounded-full gap-5"
        }
      >
        <InputBubble
          word={word}
          onWordChange={submitted ? () => undefined : setWord}
          onSubmit={handleSubmit}
        >
          <button
            className="bg-blue-700 text-sm pl-5 pr-5 hover:bg-blue-500 text-white absolute top-4 right-5 rounded-full p-3 shadow-md"
            onClick={handleSubmit}
          >
            Explore
          </button>
        </InputBubble>
        <div className={"flex flex-wrap gap-10 justify-center"}>
          <SubInputLayout>
            <YearRangeInput
              max={2021}
              min={1500}
              value={searchYearRange}
              showLabel={true}
              onChange={setSearchRange}
              placeholder={[1789, 1950]}
            />
          </SubInputLayout>
          <SubInputLayout>
            <SelectInput
              label={"corpus"}
              options={corpusOptions}
              value={source}
              onChange={(new_source) => {
                if (
                  new_source === "presse" ||
                  new_source === "livres" ||
                  new_source === "lemonde"
                ) {
                  graphStateDispatch({
                    type: "set_source",
                    payload: new_source,
                  });
                }
              }}
            />
          </SubInputLayout>
          <SubInputLayout>
            <div className={"flex flex-col"}>
              <label
                htmlFor={"link-term"}
                className="flex text-gray-700 text-sm font-bold mb-2 items-center gap-5"
              >
                {"Proximité"}
                <Image src={link} alt="link" width={25} height={25} />3
              </label>
              <input
                type="text"
                className={"border p-2 rounded-lg shadow-sm"}
                value={linkTerm}
                onChange={(e) =>
                  graphStateDispatch({
                    type: "set_link_term",
                    payload: e.target.value,
                  })
                }
              />
            </div>
          </SubInputLayout>
        </div>
      </div>
      {fetching && (
        <SearchProgress
          ticket={currentTicket}
          onFetchComplete={() => {
            onCreateTicket(currentTicket);
            reset();
          }}
          onNoRecordsFound={() => {
            alert(translation.no_records_found);
            reset();
          }}
        />
      )}
      <div className={"m-2"} />
      <TicketRow
        tickets={tickets}
        onGraphedTicketCardClick={onDeleteTicket}
        submitted={submitted}
      />
      <div className={"m-2"} />
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
      </div>
    </button>
  );
};
