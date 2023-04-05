import React, { useContext } from "react";
import { InputForm } from "../components/InputForm";
import { ResultViewer, getTicketData } from "../components/ResultViewer";
import { GallicaResponse, GraphData } from "../models/dbStructs";
import { GetServerSideProps, InferGetServerSidePropsType } from "next/types";
import { TableProps, fetchContext } from "../components/ResultsTable";
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

export const getServerSideProps: GetServerSideProps<{
  initRecords: GallicaResponse;
  initSeries: GraphData[];
  initTickets: GraphTicket[];
}> = async ({ query }) => {
  if (query.ticket_id) {
    if (!Array.isArray(query.ticket_id)) {
      query.ticket_id = [query.ticket_id];
    }
  }
  const result = graphStateURL.safeParse(query);
  let records: GallicaResponse;
  let initSeries: GraphData[];
  let initTickets: GraphTicket[];
  if (result.success) {
    const ticketsWithState = await Promise.all(
      result.data.ticket_id.map(async (ticket_id) => {
        const result = await fetch(`${apiURL}/api/ticketState/${ticket_id}`);
        return (await result.json()) as GraphTicket;
      })
    );
    const selectedTicket = ticketsWithState.find(
      (ticket) => ticket.id === result.data.context_selected_ticket
    );
    let initContextParams: TableProps = {
      terms: selectedTicket?.terms || ticketsWithState[0].terms,
      limit: 15,
      source: "periodical",
      yearRange: [
        result.data.context_year || 1789,
        result.data.context_end_year || 1950,
      ],
      month: result.data.context_month || undefined,
    };
    records = await fetchContext(0, initContextParams);
    initSeries = await Promise.all(
      ticketsWithState.map((ticket) => {
        return getTicketData(
          ticket.id,
          result.data.grouping || "year",
          result.data.smoothing || 0
        );
      })
    );
    initTickets = ticketsWithState;
  } else {
    initTickets = [
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
    ];
    const initRecordParams: TableProps = {
      terms: initTickets[0].terms,
      limit: 15,
      source: "periodical",
      yearRange: [1789, 1950],
      codes: [],
    };
    records = await fetchContext(0, initRecordParams);
    initSeries = await Promise.all(
      initTickets.map((ticket) => {
        return getTicketData(
          ticket.id,
          initGraphParams.grouping,
          initGraphParams.smoothing
        );
      })
    );
  }
  return {
    props: {
      initRecords: records,
      initSeries: initSeries,
      initTickets: initTickets,
    },
  };
};

export default function Home({
  initRecords,
  initSeries,
  initTickets,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  const [graphState, graphStateDispatch] = React.useReducer(graphStateReducer, {
    tickets: initTickets,
    contextYearRange: [1789, 1950],
    searchYearRange: [1789, 1950],
    month: undefined,
    grouping: initGraphParams.grouping,
    smoothing: initGraphParams.smoothing,
    selectedTicket: initTickets[0].id,
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
    const [start, end] = graphState.contextYearRange;
    if (start) {
      params.append("context_year", start.toString());
    }
    if (end) {
      params.append("context_end_year", end.toString());
    }
    window.history.replaceState(
      {},
      "",
      `${window.location.pathname}?${params.toString()}`
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
        <GraphAndTable initRecords={initRecords} initSeries={initSeries} />
      </GraphPageStateContext.Provider>
    </GraphPageDispatchContext.Provider>
  );
}

function GraphAndTable(props: {
  initRecords: GallicaResponse;
  initSeries: GraphData[];
}) {
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
      {tickets && tickets.length > 0 && (
        <ResultViewer
          initRecords={props.initRecords}
          initGraphData={props.initSeries}
        />
      )}
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
