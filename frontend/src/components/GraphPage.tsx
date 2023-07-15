"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Head } from "next/document";
import React, { useContext } from "react";
import {
  GraphPageDispatchContext,
  GraphPageStateContext,
} from "./GraphContext";
import { graphStateReducer, GraphPageState } from "./GraphStateReducer";
import { GraphTicket } from "./GraphTicket";
import { InputForm } from "./InputForm";
import { LangContext } from "./LangContext";
import NavBar from "./NavBar";
import { ResultViewer } from "./ResultViewer";

export function GraphPage(props: { initTickets?: GraphTicket[] }) {
  const [graphState, graphStateDispatch] = React.useReducer(graphStateReducer, {
    tickets: props.initTickets,
    contextYearRange: [undefined, undefined],
    searchYearRange: [undefined, undefined],
    month: undefined,
    grouping: initGraphParams.grouping,
    smoothing: initGraphParams.smoothing,
    selectedTicket: props.initTickets?.[0].id,
    source: "presse",
    linkTerm: undefined,
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
      <AnimatePresence>
        {tickets && tickets.length > 0 && (
          <motion.div
            key={"graph"}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <ResultViewer />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface YearRangeInputProps {
  min: number;
  max: number;
  value?: [number | undefined, number | undefined];
  placeholder?: [number, number];
  onChange: (value: [number | undefined, number | undefined]) => void;
  showLabel?: boolean;
}
export const YearRangeInput: React.FC<YearRangeInputProps> = (props) => {
  const { lang } = useContext(LangContext);
  const [expanded, setExpanded] = React.useState(false);
  const [localValue, setLocalValue] = React.useState(props.value);
  return (
    <div className={"relative"}>
      {props.showLabel && (
        <label
          htmlFor={"year-range"}
          className="block text-gray-700 text-sm font-bold"
        >
          {lang === "fr" ? "Années" : "Years"}
        </label>
      )}
      {expanded && (
        <div
          className={
            "flex flex-col text-md max-w-md items-center gap-5 p-3 border rounded-lg absolute top-0 -left-10 bg-white z-40"
          }
          id={"year-range"}
        >
          <div className={"flex gap-5 items-center"}>
            <input
              className="w-20 border p-3  rounded-md"
              type="number"
              value={localValue?.[0] || ""}
              onChange={(e) => {
                const newValue = parseInt(e.target.value);
                if (typeof newValue === "number") {
                  setLocalValue([newValue, localValue?.[1]]);
                }
              }}
              placeholder={props.placeholder?.[0].toString()}
            />
            {lang === "fr" ? "à" : "to"}
            <input
              className="w-20 p-3 rounded-md border"
              type="number"
              value={localValue?.[1] || ""}
              onChange={(e) => {
                const newValue = parseInt(e.target.value);
                if (typeof newValue === "number") {
                  setLocalValue([localValue?.[0], newValue]);
                }
              }}
              placeholder={props.placeholder?.[1].toString()}
            />
          </div>
          <div className={"flex gap-5 items-center"}>
            <button
              className={"p-2 text-blue-500"}
              onClick={() => {
                setExpanded(false);
              }}
            >
              {lang === "fr" ? "Annuler" : "Cancel"}
            </button>
            <button
              className={"border p-2 hover:bg-blue-100 rounded-md"}
              onClick={() => {
                props.onChange(localValue || [undefined, undefined]);
                setExpanded(false);
              }}
            >
              Apply
            </button>
          </div>
        </div>
      )}
      <div
        className={
          "flex flex-row text-md items-center gap-5 p-3 cursor-pointer bg-blue-100 rounded-xl"
        }
        id={"year-range"}
        onClick={() => setExpanded(true)}
      >
        <span className={""}>{props.value?.[0] || props.placeholder?.[0]}</span>
        <span className={""}>to</span>
        <span className={""}>{props.value?.[1] || props.placeholder?.[1]}</span>
        ⌄
      </div>
    </div>
  );
};
