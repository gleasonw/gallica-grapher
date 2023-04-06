import React, { useContext } from "react";
import { InputForm } from "../components/InputForm";
import { ResultViewer } from "../components/ResultViewer";
import { GetServerSideProps } from "next/types";
import {
  graphStateReducer,
  GraphPageState,
} from "../components/GraphStateReducer";
import {
  GraphPageDispatchContext,
  GraphPageStateContext,
} from "../components/GraphContext";
import { LangContext } from "../components/LangContext";
import { GraphTicket } from "../components/GraphTicket";
import NavBar from "../components/NavBar";
import { z } from "zod";
import { apiURL } from "../components/apiURL";
import Head from "next/head";
import { useRouter } from "next/router";
import { useQueries, useQuery } from "@tanstack/react-query";

const strings = {
  fr: {
    title: "The Gallica Grapher",
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
    linkTerm: "Terme de proximité",
    linkDistance: "Distance de proximité",
  },
  en: {
    title: "The Gallica Grapher",
    description: "Explore word occurrences in archived Gallica periodicals.",
    linkTerm: "Link term",
    linkDistance: "Link distance",
  },
};

const initGraphParams = {
  grouping: "year",
  smoothing: 0,
};

const graphStateURL = z.object({
  ticket_id: z.coerce.number().array(),
  context_year: z.coerce.number().nullish(),
  context_end_year: z.coerce.number().nullish(),
  context_month: z.coerce.number().nullish(),
  grouping: z.string().nullish(),
  smoothing: z.coerce.number().nullish(),
  context_selected_ticket: z.coerce.number().nullish(),
});

export default function Home() {
  // TODO: if initTickets is empty, check local storage, else use default tickets
  const router = useRouter();
  const query = router.query;
  if (query.ticket_id) {
    if (!Array.isArray(query.ticket_id)) {
      query.ticket_id = [query.ticket_id];
    }
  }
  const result = graphStateURL.safeParse(query);
  if (result.success) {
    console.log("load from remote");
    return <LoadGraphStateFromRemoteTicket urlState={result.data} />;
  } else {
    return <LoadGraphStateFromLocal />;
  }
}

function LoadGraphStateFromRemoteTicket(props: {
  urlState: typeof graphStateURL._output;
}) {
  const ticketsWithState = useQuery({
    queryKey: ["tickets"],
    queryFn: async () => {
      const ticketsWithState = await Promise.all(
        props.urlState.ticket_id.map(async (ticket_id) => {
          const result = await fetch(`${apiURL}/api/ticketState/${ticket_id}`);
          return (await result.json()) as GraphTicket;
        })
      );
      return ticketsWithState;
    },
  });
  if (ticketsWithState.status === "loading") {
    return <div>Loading...</div>;
  }
  if (!ticketsWithState.data) {
    return <div>Could not load tickets</div>;
  }
  return <GraphPage initTickets={ticketsWithState.data} />;
}

function LoadGraphStateFromLocal() {
  return (
    <GraphPage
      initTickets={[
        {
          id: 0,
          terms: ["brazza"],
          example: true,
        },
        {
          id: 1,
          terms: ["congo"],
          example: true,
        },
        {
          id: -1,
          terms: ["coloniale"],
          example: true,
        },
      ]}
    />
  );
}

function GraphPage(props: { initTickets?: GraphTicket[] }) {
  const [graphState, graphStateDispatch] = React.useReducer(graphStateReducer, {
    tickets: props.initTickets,
    contextYearRange: [1789, 1950],
    searchYearRange: [1789, 1950],
    month: undefined,
    grouping: initGraphParams.grouping,
    smoothing: initGraphParams.smoothing,
    selectedTicket: props.initTickets?.[0].id,
  } as GraphPageState);

  React.useEffect(() => {
    if (graphState.tickets?.some((ticket) => ticket.example)) {
      return;
    }
    const params = new URLSearchParams();
    if (graphState.tickets) {
      for (const ticket of graphState.tickets) {
        params.append("ticket_id", ticket.id.toString());
      }
    }
    window.history.replaceState(
      {},
      "",
      `${window.location.pathname.split("/")[0]}?${params.toString()}`
    );
  }, [graphState]);

  return (
    <GraphPageDispatchContext.Provider value={graphStateDispatch}>
      <GraphPageStateContext.Provider value={graphState}>
        <Head>
          <title>Gallica Grapher</title>
          <meta
            name="Graph word occurrences in archived French periodicals."
            content="Gallica Grapher"
          />
          <link rel="icon" href="/favicon.ico" />
        </Head>
        <NavBar />
        <GraphAndTable />
      </GraphPageStateContext.Provider>
    </GraphPageDispatchContext.Provider>
  );
}

function GraphAndTable() {
  const { lang } = React.useContext(LangContext);
  const translation = strings[lang];
  const graphState = React.useContext(GraphPageStateContext);
  if (!graphState) {
    throw new Error("Graph state not initialized");
  }
  const { tickets, contextYearRange: yearRange } = graphState;
  const graphStateDispatch = React.useContext(GraphPageDispatchContext);
  if (!graphStateDispatch) {
    throw new Error("Graph dispatch not initialized");
  }

  return (
    <div className={"flex flex-col"}>
      <title>{translation.title}</title>
      <div className="m-10 mt-20 text-center text-4xl">
        {" "}
        {translation.description}{" "}
      </div>
      <InputForm
        onCreateTicket={(ticket) =>
          graphStateDispatch({
            type: "add_ticket",
            payload: ticket,
          })
        }
        tickets={tickets}
        onDeleteTicket={(ticketID) =>
          graphStateDispatch({
            type: "remove_ticket",
            payload: ticketID,
          })
        }
        onDeleteExampleTickets={() =>
          graphStateDispatch({
            type: "remove_example_tickets",
          })
        }
      />
      {tickets && tickets.length > 0 && <ResultViewer />}
    </div>
  );
}

interface YearRangeInputProps {
  min: number;
  max: number;
  value?: [number | undefined, number | undefined];
  onChange: (value: [number | undefined, number | undefined]) => void;
  showLabel?: boolean;
}
export const YearRangeInput: React.FC<YearRangeInputProps> = (props) => {
  const { lang } = useContext(LangContext);
  return (
    <div>
      {props.showLabel && (
        <label
          htmlFor={"year-range"}
          className="block text-gray-700 text-sm font-bold mb-2"
        >
          {lang === "fr" ? "Années" : "Years"}
        </label>
      )}
      <div
        className={"flex flex-row text-md max-w-md items-center gap-10 p-3"}
        id={"year-range"}
      >
        <input
          className="w-20 border p-3  rounded-lg"
          type="number"
          value={props.value?.[0]}
          onChange={(e) => {
            const newValue = parseInt(e.target.value);
            if (typeof newValue === "number") {
              props.onChange([newValue, props.value?.[1]]);
            }
          }}
        />
        {lang === "fr" ? "à" : "to"}
        <input
          className="w-20 p-3 rounded-lg border"
          type="number"
          value={props.value?.[1]}
          onChange={(e) => {
            const newValue = parseInt(e.target.value);
            if (typeof newValue === "number") {
              props.onChange([props.value?.[0], newValue]);
            }
          }}
        />
      </div>
    </div>
  );
};
