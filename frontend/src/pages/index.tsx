import React, { useState, createContext } from "react";
import Link from "next/link";
import Image from "next/image";
import { InputForm } from "../components/InputForm";
import { ResultViewer, getTicketData } from "../components/ResultViewer";
import { GallicaResponse, GraphData, Paper } from "../models/dbStructs";
import { GetStaticProps, InferGetStaticPropsType } from "next/types";
import { fetchContext } from "../components/ResultsTable";
import Info from "../components/Info";
import { AnimatePresence, motion } from "framer-motion";

export interface Ticket {
  id: number;
  terms: string[];
  grouping: "month";
  backend_source?: "gallica" | "pyllica";
  start_date?: number;
  end_date?: number;
  papers?: Paper[];
  link_term?: string;
  link_distance?: number;
  example?: boolean;
}

export const pages = ["graph", "context", "info"] as const;

type Page = typeof pages[number];

export const initTickets = [
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
] as Ticket[];

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

export const LangContext = createContext<{
  lang: "fr" | "en";
  setLang: React.Dispatch<React.SetStateAction<"fr" | "en">>;
}>({ lang: "fr", setLang: () => {} });

const strings = {
  fr: {
    title: "The Gallica Grapher",
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
  },
  en: {
    title: "The Gallica Grapher",
    description: "Explore word occurrences in archived Gallica periodicals.",
  },
};

export default function Home({
  initRecords,
  initSeries,
}: InferGetStaticPropsType<typeof getStaticProps>) {
  const [lang, setLang] = useState<"fr" | "en">("fr");
  const [currentPage, setCurrentPage] = useState<Page>("graph");
  const [showSidebar, setShowSidebar] = React.useState(false);
  let homeLinkStyle = "p-5 hover:cursor-pointer";
  let exploreLinkStyle = "p-5 hover:cursor-pointer";
  let infoLinkStyle = "p-5 hover:cursor-pointer";
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
            <div className={"flex flex-row gap-5 align-center justify-center"}>
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
  );
}

function GraphAndTable({
  initRecords,
  initSeries,
}: InferGetStaticPropsType<typeof getStaticProps>) {
  const { lang } = React.useContext(LangContext);
  const translation = strings[lang];
  const [graphTickets, setGraphTickets] = useState<Ticket[]>(initTickets);
  const [outerRange, setOuterRange] = useState<[number, number]>([1789, 2000]);
  return (
    <>
      <title>{translation.title}</title>
      <div className="m-10 text-center text-4xl">
        {" "}
        {translation.description}{" "}
      </div>
      <InputForm
        onCreateTicket={(ticket: Ticket) => {
          const noExamples = graphTickets.filter((t) => !t.example);
          setGraphTickets([...noExamples, ticket]);
        }}
        onSliderChange={(range: [number, number]) => {
          setOuterRange(range);
        }}
        tickets={graphTickets}
        yearRange={outerRange}
        onDeleteTicket={(ticket?: Ticket) => {
          if (graphTickets && ticket) {
            setGraphTickets(graphTickets.filter((t) => t.id !== ticket.id));
          }
        }}
        onDeleteExampleTickets={() => {
          setGraphTickets(graphTickets.filter((t) => !t.example));
        }}
      />
      {graphTickets && graphTickets.length > 0 && (
        <ResultViewer
          tickets={graphTickets}
          outerRange={outerRange}
          initVals={{ initRecords, initSeries }}
        />
      )}
    </>
  );
}

function SearchableContext(props: { initRecords: GallicaResponse }) {
  const { lang } = React.useContext(LangContext);
  const [tickets, setTickets] = useState<Ticket[]>(initTickets);
  const [selectedPapers, setSelectedPapers] = useState<Paper[]>([]);
  const [month, setMonth] = useState<number | undefined>(undefined);
  const [day, setDay] = useState<number | undefined>(undefined);
  const [yearRange, setYearRange] = useState<[number, number]>([1789, 2000]);
  const [source, setSource] = useState<"book" | "periodical" | "all">("all");

  return <>Coming soon!</>;
}
