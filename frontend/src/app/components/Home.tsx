import React from "react";
import { InputForm } from "../components/InputForm";
import {
  graphStateReducer,
  GraphPageState,
} from "../components/GraphStateReducer";
import {
  GraphPageDispatchContext,
  GraphPageStateContext,
} from "../components/GraphContext";
import { LangContext } from "../components/LangContext";
import Head from "next/head";
import { AnimatePresence, motion } from "framer-motion";
import { useQueries } from "@tanstack/react-query";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import { InputLabel } from "../components/InputLabel";
import { PaperDropdown } from "../components/PaperDropdown";
import { SelectInput } from "../components/SelectInput";
import { apiURL } from "../components/apiURL";
import { makeOptions } from "../components/utils/makeHighcharts";
import { Paper, GraphData } from "./models/dbStructs";
import { OCRTable } from "./OCRTable";

const gallica_plug = (
  <a
    href="https://shiny.ens-paris-saclay.fr/app/gallicagram"
    target="_blank"
    rel="noreferrer"
    className="text-blue-500 underline"
  >
    Gallicagram
  </a>
);

const strings = {
  fr: {
    title: "The Gallica Grapher",
    description:
      "Explorez les occurrences de mots dans des périodiques Gallica.",
    linkTerm: "Terme de proximité",
    linkDistance: "Distance de proximité",
    zoom_out: "Zoomer à l'échelle originale",
    gallicagram_plug: (
      <>
        <p>
          Données de charte fournies par {gallica_plug}, un projet de Benjamin
          Azoulay et Benoît de Courson.
        </p>
      </>
    ),
    grouping: "Résolution",
    smoothing: "Lissage",
    months: [
      "Janvier",
      "Février",
      "Mars",
      "Avril",
      "Mai",
      "Juin",
      "Juillet",
      "Août",
      "Septembre",
      "Octobre",
      "Novembre",
      "Décembre",
    ],
  },
  en: {
    title: "The Gallica Grapher",
    description: "Explore word occurrences in archived Gallica periodicals.",
    linkTerm: "Link term",
    linkDistance: "Link distance",
    zoom_out: "Zoom out",
    gallicagram_plug: (
      <>
        <p>
          Chart data provided by {gallica_plug}, a project by Benjamin Azoulay
          and Benoît de Courson.
        </p>
      </>
    ),
    grouping: "Grouping",
    smoothing: "Smoothing",
    months: [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ],
  },
};

const initGraphParams = {
  grouping: "year",
  smoothing: 0,
};

const initTickets = [
  {
    id: 0,
    terms: ["brazza"],
    example: true,
    source: "presse" as const,
  },
  {
    id: 1,
    terms: ["congo"],
    example: true,
    source: "presse" as const,
  },
  {
    id: -1,
    terms: ["coloniale"],
    example: true,
    source: "presse" as const,
  },
];

export function Home() {
  const [graphState, graphStateDispatch] = React.useReducer(graphStateReducer, {
    tickets: initTickets,
    searchFrom: undefined,
    searchTo: undefined,
    month: undefined,
    grouping: initGraphParams.grouping,
    smoothing: initGraphParams.smoothing,
    selectedTicket: initTickets?.[0].id,
    source: "presse",
    linkTerm: undefined,
  } as GraphPageState);
  const [selectedPage, setSelectedPage] = React.useState(0);

  const { lang } = React.useContext(LangContext);
  const translation = strings[lang];
  const {
    tickets,
    selectedTicket,
    grouping,
    smoothing,
    month,
    searchFrom,
    searchTo,
  } = graphState;

  const chartComponentRef = React.useRef<HighchartsReact.RefObject>(null);

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

  React.useEffect(() => {
    function updateExtremes(from: number, to: number) {
      const chart = chartComponentRef.current?.chart;
      chart?.xAxis[0].setExtremes(Date.UTC(from, 0, 1), Date.UTC(to, 11, 31));
      chart?.showResetZoom();
    }
    if (chartComponentRef.current) {
      const chart = chartComponentRef.current.chart;
      if (chart) {
        if (searchFrom && searchTo) {
          updateExtremes(searchFrom, searchTo);
        } else if (searchFrom) {
          updateExtremes(searchFrom, 1950);
        } else if (searchTo) {
          updateExtremes(1789, searchTo);
        } else {
          chart.xAxis[0].setExtremes(undefined, undefined);
        }
      }
    }
  }, [searchFrom, searchTo]);

  function setSelectedTicket(ticketID?: number) {
    graphStateDispatch!({
      type: "set_selected_ticket",
      payload: ticketID,
    });
  }

  function setGrouping(grouping: "year" | "month") {
    graphStateDispatch!({
      type: "set_grouping",
      payload: grouping,
    });
  }

  function setSmoothing(smoothing: number) {
    graphStateDispatch!({
      type: "set_smoothing",
      payload: smoothing,
    });
  }

  function setMonth(month: number | undefined) {
    graphStateDispatch!({
      type: "set_month",
      payload: month,
    });
  }

  function setSearchFrom(from: number | undefined) {
    graphStateDispatch!({
      type: "set_search_from",
      payload: from,
    });
  }

  function setSearchTo(to: number | undefined) {
    graphStateDispatch!({
      type: "set_search_to",
      payload: to,
    });
  }

  function handleSeriesClick(point: Highcharts.Point) {
    if (!graphStateDispatch) return;
    const correspondingTicket = tickets?.find(
      (t) => t.terms[0] === point.series.name
    );
    if (correspondingTicket) {
      setSelectedTicket(correspondingTicket.id);
    }
    const date = new Date(point.category);
    if (grouping === "year") {
      setMonth(undefined);
    } else {
      setMonth(date.getUTCMonth() + 1);
    }
    setSearchFrom(date.getUTCFullYear());
    setSearchTo(date.getUTCFullYear() + 1);
  }

  function handleSetExtremes(e: Highcharts.AxisSetExtremesEventObject) {
    if (!graphStateDispatch) return;
    if (e.trigger === "zoom") {
      const minDate = new Date(e.min);
      const maxDate = new Date(e.max);
      if (minDate.toString() === "Invalid Date") {
        setMonth(undefined);
        setSearchFrom(undefined);
        setSearchTo(undefined);
        return;
      }
      if (grouping === "month") {
        setMonth(minDate.getUTCMonth() + 1);
      }
      setSearchFrom(minDate.getUTCFullYear());
      setSearchTo(maxDate.getUTCFullYear());
    }
  }

  const thereAreTickets = tickets && tickets.length > 0;
  const [selectedPapers, setSelectedPapers] = React.useState<
    Paper[] | undefined
  >();

  if (
    tickets &&
    tickets.length > 0 &&
    !tickets.some((t) => t.id === selectedTicket)
  ) {
    setSelectedTicket(tickets[0].id);
    setMonth(undefined);
    setSearchFrom(undefined);
    setSearchTo(undefined);
  }

  async function getTicketData(
    id: number,
    grouping: string,
    smoothing: number
  ) {
    const response = await fetch(
      `${apiURL}/api/graphData?request_id=${id}&backend_source=pyllica&grouping=${grouping}&average_window=${smoothing}`
    );
    const data = (await response.json()) as GraphData;
    return data;
  }

  const ticketData = useQueries({
    queries:
      tickets?.map((ticket) => {
        const { id } = ticket;
        return {
          queryKey: ["ticket", { id, grouping, smoothing }],
          queryFn: () => getTicketData(ticket.id, grouping, smoothing),
          keepPreviousData: true,
        };
      }) ?? [],
  });
  ``;
  const highchartsOpts = makeOptions(
    handleSetExtremes,
    handleSeriesClick,
    ticketData
  );

  console.log({ highchartsOpts });

  function resetSearchRange() {
    setSearchFrom(undefined);
    setSearchTo(undefined);
  }

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
            {highchartsOpts.series && (
              <motion.div
                key={"graph"}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className={"h-full w-full bg-white"}>
                  <div className={"relative"}>
                    <div
                      className={
                        "ml-10 absolute -top-20 right-2 z-40 mb-5 flex flex-row gap-5"
                      }
                    >
                      <InputLabel label={translation.grouping}>
                        <SelectInput
                          options={["year", "month"]}
                          onChange={(value: string) =>
                            setGrouping(value as "year" | "month")
                          }
                          value={grouping}
                        />
                      </InputLabel>
                      <InputLabel label={translation.smoothing}>
                        <SelectInput
                          options={[
                            "0",
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                            "10",
                            "20",
                            "50",
                          ]}
                          onChange={(value: string) =>
                            setSmoothing(parseInt(value))
                          }
                          value={smoothing.toString()}
                        />
                      </InputLabel>
                    </div>
                    <HighchartsReact
                      highcharts={Highcharts}
                      options={highchartsOpts}
                      ref={chartComponentRef}
                    />
                  </div>
                  <div className={"flex flex-col gap-5 ml-5 mr-5 mt-2"}>
                    {translation.gallicagram_plug}
                    <div className={"flex wrap gap-10"}>
                      <SelectInput
                        options={
                          tickets?.map((ticket) => ticket.terms[0]) ?? []
                        }
                        onChange={(value: string) =>
                          setSelectedTicket(
                            tickets?.filter((t) => t.terms[0] === value)[0].id
                          )
                        }
                        value={
                          tickets?.filter((t) => t.id === selectedTicket)?.[0]
                            ?.terms[0]
                        }
                      />
                      <ContextFilter
                        label={
                          searchFrom && searchTo
                            ? `${searchFrom} - ${searchTo}`
                            : undefined
                        }
                        onClick={resetSearchRange}
                      />
                      <ContextFilter
                        label={
                          month ? translation.months[month - 1] : undefined
                        }
                        onClick={() => setMonth(undefined)}
                      />
                    </div>
                  </div>
                  <OCRTable
                    selectedPage={selectedPage}
                    onSelectedPageChange={setSelectedPage}
                    terms={
                      (thereAreTickets &&
                        tickets!.filter((t) => t.id === selectedTicket)[0]
                          ?.terms) ||
                      []
                    }
                    link_term={
                      thereAreTickets
                        ? tickets?.find((t) => t.id === selectedTicket)
                            ?.linkTerm
                        : undefined
                    }
                    link_distance={3}
                    codes={selectedPapers?.map((p) => p.code) || []}
                    month={month}
                    yearRange={[searchFrom, searchTo]}
                    source="periodical"
                  >
                    <div
                      className={
                        "flex flex-row flex-wrap gap-5 md:gap-10 lg:gap-10"
                      }
                    >
                      <InputLabel label={lang === "fr" ? "Année" : "Year"}>
                        <input
                          type={"number"}
                          className={"border rounded-lg bg-white p-3"}
                          value={searchFrom || ""}
                          onChange={(e) => {
                            setSearchFrom(parseInt(e.target.value));
                            if (
                              searchTo &&
                              parseInt(e.target.value) > searchTo
                            ) {
                              setSearchTo(parseInt(e.target.value));
                            }
                          }}
                        />
                      </InputLabel>
                      <InputLabel label={lang === "fr" ? "Mois" : "Month"}>
                        <SelectInput
                          options={Array.from(Array(12).keys()).map((i) =>
                            String(i)
                          )}
                          onChange={(value) => setMonth(parseInt(value))}
                          value={month ? String(month) : undefined}
                        />
                      </InputLabel>
                      <InputLabel label={"Ticket"}>
                        <select
                          onChange={(e) => {
                            setSelectedTicket(parseInt(e.target.value));
                          }}
                          className={"border rounded-lg  bg-white p-3"}
                          value={selectedTicket || ""}
                        >
                          {tickets?.map((ticket) => (
                            <option key={ticket.id} value={ticket.id}>
                              {ticket.terms}
                            </option>
                          ))}
                        </select>
                      </InputLabel>
                      <InputLabel
                        label={lang === "fr" ? "Périodique" : "Periodical"}
                      >
                        <PaperDropdown
                          onClick={(paper) => {
                            if (selectedPapers) {
                              setSelectedPapers([...selectedPapers, paper]);
                            } else {
                              setSelectedPapers([paper]);
                            }
                          }}
                        />
                      </InputLabel>
                    </div>
                    <div className={"flex flex-row flex-wrap"}>
                      {selectedPapers?.map((paper) => (
                        <button
                          onClick={() => {
                            if (selectedPapers) {
                              setSelectedPapers(
                                selectedPapers.filter(
                                  (p) => p.code !== paper.code
                                )
                              );
                            }
                          }}
                          key={paper.code}
                          className={
                            "m-5 ml-0 mb-0 border p-5 hover:bg-zinc-100"
                          }
                        >
                          {paper.title}
                        </button>
                      ))}
                    </div>
                  </OCRTable>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </GraphPageStateContext.Provider>
    </GraphPageDispatchContext.Provider>
  );
}

function ContextFilter({
  label,
  onClick,
}: {
  label: any;
  onClick: () => void;
}) {
  if (!label) {
    return <></>;
  }
  return (
    <div className={"flex flex-row gap-2"}>
      <button
        className={
          "flex flex-row gap-5 items-center border shadow-md rounded-md p-3 hover:bg-zinc-100"
        }
        onClick={onClick}
      >
        <div>{label}</div>
        <div>X</div>
      </button>
    </div>
  );
}
