import React, { useState, useContext } from "react";
import Link from "next/link";
import Image from "next/image";
import { InputForm } from "../components/InputForm";
import { ResultViewer, getTicketData } from "../components/ResultViewer";
import { GallicaResponse, GraphData, Paper } from "../models/dbStructs";
import { GetStaticProps, InferGetStaticPropsType } from "next/types";
import { ResultsTable, fetchContext } from "../components/ResultsTable";
import Info from "../components/Info";
import { AnimatePresence, motion } from "framer-motion";
import {
  graphStateReducer,
  GraphPageState,
} from "../components/GraphStateReducer";
import {
  GraphPageDispatchContext,
  GraphPageStateContext,
} from "../components/GraphContext";
import {
  SearchPageDispatchContext,
  SearchPageStateContext,
} from "../components/SearchContext";
import {
  SearchPageState,
  searchStateReducer,
} from "../components/SearchStateReducer";
import InputBubble from "../components/InputBubble";
import DashboardLayout from "../components/DashboardLayout";
import { PaperSelector } from "../components/PaperSelector";
import { SelectInput } from "../components/SelectInput";

import { GraphTicket, initTickets } from "./GraphTicket";
import { LangContext, strings } from "./LangContext";
import link from "../components/assets/link.svg";
import refresh from "../components/assets/refresh.svg";

type Page = "graph" | "context" | "info";

export const getStaticProps: GetStaticProps<{
  initRecords: GallicaResponse;
  initSeries: GraphData[];
}> = async () => {
  const records = await fetchContext(0, {
    terms: initTickets[0].terms,
    limit: 10,
    source: "periodical",
  });
  const initSeries = await Promise.all(
    initTickets.map((ticket) => {
      return getTicketData(ticket.id, ticket.backend_source, "year", 0);
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
  const [lang, setLang] = useState<"fr" | "en">("fr");
  const [currentPage, setCurrentPage] = useState<Page>("graph");
  const [showSidebar, setShowSidebar] = React.useState(false);

  const [graphState, graphStateDispatch] = React.useReducer(graphStateReducer, {
    tickets: initTickets,
    yearRange: [1750, 2020],
    month: undefined,
    grouping: "year",
    smoothing: 0,
    selectedTicket: undefined,
  } as GraphPageState);

  const [searchState, searchStateDispatch] = React.useReducer(
    searchStateReducer,
    {
      term: "",
      papers: undefined,
      source: "all",
      limit: 10,
      cursor: 0,
      yearRange: [undefined, undefined],
      sort: "relevance",
      linkTerm: undefined,
      linkDistance: 0,
    } as SearchPageState
  );

  const linkStyle = "p-5 hover:cursor-pointer";
  let homeLinkStyle = linkStyle;
  let exploreLinkStyle = linkStyle;
  let infoLinkStyle = linkStyle;
  const borderBottomFocus = " border-b border-blue-500 border-b-4";
  if (currentPage === "graph") {
    homeLinkStyle += borderBottomFocus;
  } else if (currentPage === "context") {
    exploreLinkStyle += borderBottomFocus;
  } else if (currentPage === "info") {
    infoLinkStyle += borderBottomFocus;
  }

  function getPage() {
    switch (currentPage) {
      case "graph":
        return (
          <GraphAndTable initRecords={initRecords} initSeries={initSeries} />
        );
      case "context":
        return <SearchableContext initRecords={initRecords} />;
      case "info":
        return <Info />;
    }
  }

  return (
    <GraphPageDispatchContext.Provider value={graphStateDispatch}>
      <GraphPageStateContext.Provider value={graphState}>
        <SearchPageDispatchContext.Provider value={searchStateDispatch}>
          <SearchPageStateContext.Provider value={searchState}>
            <LangContext.Provider value={{ lang, setLang }}>
              <div className="flex flex-col">
                <div className="flex flex-col sticky top-0 z-50">
                  <div
                    className={
                      "flex flex-row items-center justify-between p-5 border-b-2 bg-white shadow-sm"
                    }
                  >
                    <div className={"flex"}>
                      <svg
                        focusable="false"
                        viewBox="0 0 24 24"
                        className="w-10 hover:cursor-pointer hover:bg-zinc-100 rounded-full"
                        onClick={() => setShowSidebar(!showSidebar)}
                      >
                        <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path>
                      </svg>
                      <div
                        className={"p-5 text-3xl"}
                        onClick={() => setCurrentPage("graph")}
                      >
                        Gallica Grapher
                      </div>
                      <div className="hidden lg:flex xl:flex items-center">
                        <div
                          className={homeLinkStyle}
                          onClick={() => setCurrentPage("graph")}
                        >
                          Graph
                        </div>
                        <div
                          className={exploreLinkStyle}
                          onClick={() => setCurrentPage("context")}
                        >
                          Context
                        </div>
                        <div
                          onClick={() => setCurrentPage("info")}
                          className={infoLinkStyle}
                        >
                          Info
                        </div>
                      </div>
                    </div>
                    <div
                      className={
                        "flex flex-row gap-5 align-center justify-center"
                      }
                    >
                      <select
                        onChange={() => setLang(lang === "fr" ? "en" : "fr")}
                        value={lang}
                        className={""}
                      >
                        <option value="fr">Français</option>
                        <option value="en">English</option>
                      </select>
                      <Link
                        href={"https://github.com/gleasonw/gallica-grapher"}
                        target={"_blank"}
                      >
                        <Image
                          src={"/github.svg"}
                          width={40}
                          height={40}
                          alt={"Github"}
                        />
                      </Link>
                    </div>
                  </div>
                  <AnimatePresence>
                    {showSidebar && (
                      <motion.div
                        initial={{ x: -1000 }}
                        animate={{ x: 0 }}
                        exit={{ x: -1000 }}
                        transition={{ duration: 0.2 }}
                        className={"sticky top-0"}
                      >
                        <div
                          className={
                            "absolute bg-white z-40 flex flex-col gap-1 p-2 h-screen border-r shadow-md"
                          }
                        >
                          <div
                            className={
                              "p-5 w-60 hover:bg-blue-100 rounded-lg hover:cursor-pointer"
                            }
                            onClick={() => setCurrentPage("graph")}
                          >
                            Graph
                          </div>
                          <div
                            className={
                              "p-5 w-60 hover:bg-blue-100 rounded-lg hover:cursor-pointer"
                            }
                            onClick={() => setCurrentPage("context")}
                          >
                            Context
                          </div>
                          <div
                            onClick={() => setCurrentPage("info")}
                            className={
                              "p-5 w-60 hover:bg-blue-100 rounded-lg hover:cursor-pointer"
                            }
                          >
                            Info
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
                <div onClick={() => setShowSidebar(false)}>{getPage()}</div>
              </div>
            </LangContext.Provider>
          </SearchPageStateContext.Provider>
        </SearchPageDispatchContext.Provider>
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
  const { tickets, yearRange } = graphState;
  const graphStateDispatch = React.useContext(GraphPageDispatchContext);

  function handleCreateTicket(ticket: GraphTicket) {
    if (graphStateDispatch) {
      graphStateDispatch({
        type: "add_ticket",
        payload: ticket,
      });
    }
  }

  function handleDeleteTicket(ticketID: number) {
    if (graphStateDispatch) {
      graphStateDispatch({
        type: "remove_ticket",
        payload: ticketID,
      });
    }
  }

  function handleDeleteExampleTickets() {
    if (graphStateDispatch) {
      graphStateDispatch({
        type: "remove_example_tickets",
      });
    }
  }

  return (
    <>
      <title>{translation.title}</title>
      <div className="m-10 text-center text-4xl">
        {" "}
        {translation.description}{" "}
      </div>
      <InputForm
        onCreateTicket={handleCreateTicket}
        tickets={tickets}
        yearRange={yearRange}
        onDeleteTicket={handleDeleteTicket}
        onDeleteExampleTickets={handleDeleteExampleTickets}
      />
      {tickets && tickets.length > 0 && (
        <ResultViewer
          tickets={tickets}
          outerRange={yearRange}
          initVals={{ initRecords, initSeries }}
        />
      )}
    </>
  );
}

function SearchableContext(props: { initRecords: GallicaResponse }) {
  const { lang } = React.useContext(LangContext);
  const translation = strings[lang];
  const searchState = React.useContext(SearchPageStateContext);
  const searchStateDispatch = React.useContext(SearchPageDispatchContext);

  if (!searchState || !searchStateDispatch) {
    throw new Error("Search state not initialized");
  }
  const {
    yearRange,
    source,
    papers,
    limit,
    cursor,
    linkTerm,
    linkDistance,
    sort,
    term,
  } = searchState;

  function makeDisplayCQL() {
    let termCQL = "";
    let dateCQL = "";
    let corpusCQL = "";
    if (term) {
      if (linkTerm) {
        termCQL = `text adj "${term}" prox/unit=word/distance=${linkDistance} "${linkTerm}"`;
      } else {
        termCQL = `text adj "${term}"`;
      }
    }
    if (yearRange[0] && yearRange[1]) {
      dateCQL = `gallicapublication_date>="${yearRange[0]}-01-01" and gallicapublication_date<="${yearRange[1]}-12-31"`;
    }
    if (papers) {
      const formattedCodes = papers.map((paper) => `${paper.code}_date`);
      corpusCQL =
        'arkPress adj "' + formattedCodes.join('" or arkPress adj "') + '"';
      if (source === "periodical") {
        corpusCQL += ' and dc.type all "fascicule"';
      } else if (source === "book") {
        corpusCQL += ' and dc.type all "monographie"';
      }
    }
    const cql = [termCQL, dateCQL, corpusCQL]
      .filter((cql) => cql !== "")
      .join(" and ");
    if (sort === "date") {
      return `${cql} sortby dc.date/sort.ascending`;
    }
    return cql;
  }

  return (
    <>
      <DashboardLayout>
        <div
          className={
            "w-full flex flex-col justify-center gap-5 items-center bg-blue-100 rounded-lg pt-5 pb-5"
          }
        >
          <InputBubble
            word={term}
            onWordChange={(word) =>
              searchStateDispatch({
                type: "set_terms",
                payload: word,
              })
            }
          />
          <SubInputLayout>
            <ProximitySearchInput
              linkTerm={linkTerm}
              linkDistance={linkDistance}
              onSetLinkDistance={(new_distance) =>
                searchStateDispatch({
                  type: "set_link_distance",
                  payload: new_distance,
                })
              }
              onSetLinkTerm={(new_term) =>
                searchStateDispatch({
                  type: "set_link_term",
                  payload: new_term,
                })
              }
            />
          </SubInputLayout>
          <SubInputLayout>
            <YearRangeInput
              min={1500}
              max={2023}
              value={yearRange}
              onChange={(value) =>
                searchStateDispatch({ type: "set_year_range", payload: value })
              }
            />
          </SubInputLayout>
          <SubInputLayout>
            <SelectInput
              label={"corpus"}
              options={["book", "periodical", "all"]}
              value={source}
              onChange={(new_source) => {
                if (
                  new_source === "book" ||
                  new_source === "periodical" ||
                  new_source === "all"
                ) {
                  searchStateDispatch({
                    type: "set_source",
                    payload: new_source,
                  });
                }
              }}
            />
            {source === "periodical" && (
              <PaperSelector
                papers={papers}
                from={yearRange[0]}
                to={yearRange[1]}
                onPaperAdd={(new_paper) =>
                  searchStateDispatch({
                    type: "add_paper",
                    payload: new_paper,
                  })
                }
                onPaperClick={(paperCode) => {
                  searchStateDispatch({
                    type: "remove_paper",
                    payload: paperCode.code,
                  });
                }}
              />
            )}
          </SubInputLayout>
          <SubInputLayout>
            <SelectInput
              label={"sort"}
              value={sort}
              options={["date", "relevance"]}
              onChange={(new_sort) => {
                if (new_sort === "date" || new_sort === "relevance") {
                  searchStateDispatch({ type: "set_sort", payload: new_sort });
                }
              }}
            />
            <SelectInput
              label={"limit"}
              value={limit}
              options={[10, 20, 50, 100]}
              onChange={(new_limit) => {
                if (typeof new_limit === "number") {
                  searchStateDispatch({
                    type: "set_limit",
                    payload: new_limit,
                  });
                }
              }}
            />
          </SubInputLayout>
          <SubInputLayout>
            <div className="flex justify-between w-full">
              <span>{makeDisplayCQL()}</span>
              <button
                className="bg-blue-500 border w-52 rounded-full p-5 shadow-md"
                onClick={() => console.log(searchState)}
              >
                RUN
              </button>
            </div>
          </SubInputLayout>
        </div>
      </DashboardLayout>
    </>
  );
}

function ProximitySearchInput(props: {
  onSetLinkTerm: (linkTerm: string) => void;
  onSetLinkDistance: (linkDistance: number) => void;
  linkTerm?: string;
  linkDistance?: number;
}) {
  const { lang } = React.useContext(LangContext);
  const translation = strings[lang];
  return (
    <div className="flex flex-wrap gap-5">
      <Image src={link} alt={"proximity search icon"} width={30} height={30} />
      <input
        type="text"
        value={props.linkTerm}
        onChange={(e) => props.onSetLinkTerm(e.target.value)}
        className={"border p-2 rounded-lg shadow-sm"}
        placeholder={translation.linkTerm}
      />
      <input
        type="number"
        value={props.linkDistance}
        onChange={(e) => props.onSetLinkDistance(Number(e.target.value))}
        className={"border p-2 rounded-lg shadow-sm"}
        placeholder={translation.linkDistance}
      />
    </div>
  );
}

interface YearRangeInputProps {
  min: number;
  max: number;
  value: [number | undefined, number | undefined];
  onChange: (value: [number | undefined, number | undefined]) => void;
}
export const YearRangeInput: React.FC<YearRangeInputProps> = (props) => {
  const { lang } = useContext(LangContext);
  return (
    <div>
      <label
        htmlFor={"year-range"}
        className="block text-gray-700 text-sm font-bold mb-2"
      >
        {lang === "fr" ? "Années" : "Years"}
      </label>
      <div
        className={
          "flex flex-row text-md max-w-md flex-wrap gap-10 p-3 border rounded-lg shadow-sm"
        }
        id={"year-range"}
      >
        <input
          className="w-20 border rounded-lg"
          type="number"
          value={props.value[0]}
          onChange={(e) => {
            const newValue = [parseInt(e.target.value), props.value[1]] as [
              number,
              number
            ];
            props.onChange(newValue);
          }}
        />
        {lang === "fr" ? "à" : "to"}
        <input
          className="w-20 rounded-lg border"
          type="number"
          value={props.value[1]}
          onChange={(e) => {
            const newValue = [props.value[0], parseInt(e.target.value)] as [
              number,
              number
            ];
            props.onChange(newValue);
          }}
        />
      </div>
    </div>
  );
};

function SubInputLayout(props: { children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap gap-5 items-center rounded-lg bg-white p-3 shadow-sm border">
      {props.children}
    </div>
  );
}
