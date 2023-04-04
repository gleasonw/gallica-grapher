import React, { useContext } from "react";
import { InputForm } from "../components/InputForm";
import { ResultViewer, getTicketData } from "../components/ResultViewer";
import { GallicaResponse, GraphData, Paper } from "../models/dbStructs";
import { GetStaticProps, InferGetStaticPropsType } from "next/types";
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

const initTickets = [
  {
    id: 0,
    terms: ["brazza"],
    grouping: "month",
    example: true,
  },
  {
    id: 1,
    terms: ["congo"],
    grouping: "month",
    example: true,
  },
  {
    id: -1,
    terms: ["coloniale"],
    grouping: "month",
    example: true,
  },
] as GraphTicket[];
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

const initRecordParams : TableProps = {
  terms: initTickets[0].terms,
  limit: 15,
  source: "periodical",
  yearRange: [1789, 1950],
  codes: [],
  nonsense: 0
};

const initGraphParams = {
  grouping: "year",
  smoothing: 0,
};

export const getStaticProps: GetStaticProps<{
  initRecords: GallicaResponse;
  initSeries: GraphData[];
}> = async () => {
  const records = await fetchContext(0, initRecordParams);
  const initSeries = await Promise.all(
    initTickets.map((ticket) => {
      return getTicketData(
        ticket.id,
        ticket.backend_source,
        initGraphParams.grouping,
        initGraphParams.smoothing
      );
    })
  );
  return {
    props: {
      initRecords: records,
      initSeries: initSeries,
    },
  };
};

export default function Home({
  initRecords,
  initSeries,
}: InferGetStaticPropsType<typeof getStaticProps>) {
  const [graphState, graphStateDispatch] = React.useReducer(graphStateReducer, {
    tickets: initTickets,
    contextYearRange: [1789, 1950],
    searchYearRange: [1789, 1950],
    month: undefined,
    grouping: "year",
    smoothing: 0,
    selectedTicket: initTickets[0].id,
  } as GraphPageState);
  const [count, setCount] = React.useState(0);

  return (
    <GraphPageDispatchContext.Provider value={graphStateDispatch}>
      <GraphPageStateContext.Provider value={graphState}>
        <NavBar />
        <GraphAndTable initRecords={initRecords} initSeries={initSeries} />
      </GraphPageStateContext.Provider>
    </GraphPageDispatchContext.Provider>
  );
}

function GraphAndTable({
  initRecords,
  initSeries,
}: InferGetStaticPropsType<typeof getStaticProps>) {
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
          initRecords={{
            key: Object.values({
              ...initRecordParams,
              terms: initRecordParams.terms,
            }),
            data: initRecords,
          }}
          initGraphData={{
            key: ["year", 0],
            data: initSeries,
          }}
        />
      )}
    </div>
  );
}

interface YearRangeInputProps {
  min: number;
  max: number;
  value: [number | undefined, number | undefined];
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
          value={props.value[0]}
          onChange={(e) => {
            const newValue = parseInt(e.target.value);
            if (typeof newValue === "number") {
              props.onChange([newValue, props.value[1]]);
            }
          }}
        />
        {lang === "fr" ? "à" : "to"}
        <input
          className="w-20 p-3 rounded-lg border"
          type="number"
          value={props.value[1]}
          onChange={(e) => {
            const newValue = parseInt(e.target.value);
            if (typeof newValue === "number") {
              props.onChange([props.value[0], newValue]);
            }
          }}
        />
      </div>
    </div>
  );
};
