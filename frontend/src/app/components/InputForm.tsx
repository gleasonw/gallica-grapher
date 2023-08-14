"use client";

import React, { useState } from "react";
import { GraphTicket } from "./GraphTicket";
import { SearchProgress } from "./SearchProgress";
import { seriesColors } from "./utils/makeHighcharts";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiURL } from "./apiURL";
import { useContext } from "react";
import { LangContext } from "./LangContext";
import { Spinner } from "./Spinner";
import InputBubble from "./InputBubble";
import DashboardLayout from "./DashboardLayout";
import { YearRangeInput } from "./YearRangeInput";
import {
  GraphPageDispatchContext,
  GraphPageStateContext,
} from "./GraphContext";
import { SelectInput } from "./SelectInput";
import { GraphData } from "./models/dbStructs";

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

interface TicketToPost extends Omit<GraphTicket, "id"> {
  id?: number;
  replacingTicketID?: number;
}

interface FetchingTicket extends GraphTicket {
  replacingTicketID?: number;
}

export function GraphSeriesForm() {
  const [word, setWord] = useState<string>("");

  const [fetchingTickets, setFetchingTickets] = useState<FetchingTicket[]>([]);
  const [refetching, setRefetching] = useState<boolean>(false);
  const [submitted, setSubmitted] = useState<boolean>(false);
  const { lang } = useContext(LangContext);
  const translation = strings[lang];

  const queryClient = useQueryClient();

  const graphStateDispatch = React.useContext(GraphPageDispatchContext);
  const graphState = React.useContext(GraphPageStateContext);
  if (!graphStateDispatch || !graphState)
    throw new Error("No graph state dispatch found");
  const { searchFrom, searchTo, source, linkTerm, grouping, smoothing } =
    graphState;

  async function setSearchRange(newRange?: [number?, number?]) {
    let [newLow, newHigh] = newRange ?? [];
    let fromBound = searchFrom ?? 1789;
    let toBound = searchTo ?? 1950;
    if ((newLow && newLow < fromBound) || (newHigh && newHigh > toBound)) {
      // check if the current tickets have the data already
      // prevents refetching data if we're just changing the zoom
      const ticketData = queryClient.getQueryData([
        "ticket",
        { id: tickets?.[0]?.id, grouping, smoothing },
      ]) as GraphData;
      if (ticketData) {
        const lowUnix = ticketData.data[0][0];
        const highUnix = ticketData.data[ticketData.data.length - 1][0];
        const lowYear = new Date(lowUnix).getFullYear() - 1;
        const highYear = new Date(highUnix).getFullYear() + 1;
        if ((newLow && newLow < lowYear) || (newHigh && newHigh > highYear)) {
          const ticketsWithNewRange: TicketToPost[] | undefined = tickets?.map(
            (ticket) => ({
              ...ticket,
              id: undefined,
              replacingTicketID: ticket.id,
              start_date: newLow || ticket.start_date,
              end_date: newHigh || ticket.end_date,
            })
          );

          if (ticketsWithNewRange) {
            setRefetching(true);
            handlePost(ticketsWithNewRange);
          }
        }
      }
    }
    graphStateDispatch!({
      type: "set_search_from",
      payload: newLow,
    });
    graphStateDispatch!({
      type: "set_search_to",
      payload: newHigh,
    });
  }

  async function postTicket(ticket: TicketToPost): Promise<FetchingTicket> {
    const response = await fetch(`${apiURL}/api/init`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ...ticket, link_term: ticket.linkTerm }),
    });
    const data = (await response.json()) as { requestid: number };
    return { ...ticket, id: data.requestid };
  }

  const mutation = useMutation({ mutationFn: postTicket });

  async function handlePost(ticketBatch: TicketToPost[]) {
    const responseTickets = await Promise.all(
      ticketBatch?.map((ticket) => mutation.mutateAsync(ticket)) || []
    );
    setFetchingTickets(responseTickets);
  }

  function reset() {
    setRefetching(false);
    setSubmitted(false);
    setFetchingTickets([]);
  }

  const ticketInForm: TicketToPost = {
    terms: [word],
    start_date: searchFrom,
    end_date: searchTo,
    source,
    linkTerm,
  };

  function handleSubmit() {
    if (!word) return;
    setSubmitted(true);
    setWord("");
    handlePost([ticketInForm]);
  }

  const corpusOptions: GraphTicket["source"][] = ["presse", "livres"];

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
        <div className={"flex flex-wrap gap-10 items-center justify-center"}>
          <YearRangeInput
            max={2021}
            min={1500}
            value={[searchFrom, searchTo]}
            onChange={setSearchRange}
            placeholder={[1789, 1950]}
          />
          <SelectInput
            options={corpusOptions}
            value={source}
            onChange={(new_source) => {
              graphStateDispatch({
                type: "set_source",
                payload: new_source as GraphTicket["source"],
              });
            }}
          />
          <input
            type="text"
            className={"border p-2 rounded-lg shadow-sm"}
            value={linkTerm}
            placeholder={"Proximité (3)"}
            onChange={(e) =>
              graphStateDispatch({
                type: "set_link_term",
                payload: e.target.value,
              })
            }
          />
        </div>
      </div>
      <div className={"m-2"} />
      {fetchingTickets && fetchingTickets.length > 0 && (
        <SearchProgress
          batchTicket={fetchingTickets}
          onFetchComplete={() => {
            for (let i = 0; i < fetchingTickets.length; i++) {
              const ticket = fetchingTickets[i];
              if (ticket.replacingTicketID) {
                onDeleteTicket(ticket.replacingTicketID);
              }
              onCreateTicket(ticket);
            }
            onDeleteExampleTickets();
            reset();
          }}
          onNoRecordsFound={() => {
            reset();
            alert(translation.no_records_found);
          }}
          onError={() => {
            reset();
            alert(
              "Probleme de connexion avec Gallicagram... Veuillez réessayer plus tard !"
            );
          }}
        />
      )}
      <TicketRow
        tickets={tickets}
        refetching={refetching}
        submitted={submitted}
        onGraphedTicketCardClick={onDeleteTicket}
      />
      <div className={"m-2"} />
    </DashboardLayout>
  );
}

function TicketRow(props: {
  tickets?: GraphTicket[];
  children?: React.ReactNode;
  onGraphedTicketCardClick: (ticketID: number) => void;
  submitted: boolean;
  refetching: boolean;
}) {
  return (
    <div className={"z-0 flex self-start"}>
      <div className={"flex flex-wrap gap-10"}>
        {props.tickets?.map((ticket, index) =>
          props.refetching ? (
            <ColorBubble
              key={ticket.id}
              color={seriesColors[index % seriesColors.length]}
            >
              <Spinner isFetching />
            </ColorBubble>
          ) : (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
              onClick={props.onGraphedTicketCardClick}
              color={seriesColors[index % seriesColors.length]}
              refetching={props.refetching}
            />
          )
        )}
        {props.submitted && (
          <ColorBubble
            color={
              seriesColors[props.tickets?.length || 0 % seriesColors.length]
            }
          >
            <Spinner isFetching />
          </ColorBubble>
        )}
      </div>
      {props.children}
    </div>
  );
}

function ColorBubble(props: { color: string; children: React.ReactNode }) {
  return (
    <div
      className={"rounded-lg border-2 bg-white p-3 text-xl shadow-md"}
      style={{
        borderColor: props.color,
      }}
    >
      {props.children}
    </div>
  );
}

interface TicketProps {
  ticket: GraphTicket;
  onClick: (ticketID: number) => void;
  color?: string;
  refetching?: boolean;
}

const TicketCard: React.FC<TicketProps> = ({ ticket, onClick, color }) => {
  return (
    <button
      onClick={() => onClick(ticket.id)}
      className={`rounded-lg border-2 bg-white p-3 text-xl shadow-md transition duration-150 hover:bg-zinc-500 hover:ease-in`}
      style={{ borderColor: color }}
    >
      <div className={`relative h-full w-full flex flex-col`}>
        <div className={"flex flex-row gap-10"}>
          <p>{ticket.terms.join(", ")}</p>
          <p className={"text-zinc-600"}>x</p>
        </div>
      </div>
    </button>
  );
};
