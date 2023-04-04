import React, { useContext } from "react";
import { LangContext } from "./LangContext";
import { getStaticProps } from "../pages/index";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { useQueries, useQuery } from "@tanstack/react-query";
import { TicketResultTable } from "./TicketResultTable";
import { apiURL } from "./apiURL";
import { FrequentTerm, GallicaResponse, GraphData } from "../models/dbStructs";
import { makeOptions } from "./utils/makeHighcharts";
import {
  GraphPageDispatchContext,
  GraphPageStateContext,
} from "./GraphContext";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";

interface ResultViewerProps {
  initRecords: GallicaResponse;
  initGraphData: GraphData[];
}

export async function getTicketData(
  id: number,
  backend_source: "gallica" | "pyllica" = "pyllica",
  grouping: string,
  smoothing: number
) {
  const response = await fetch(
    `${apiURL}/api/graphData?request_id=${id}&backend_source=${backend_source}&grouping=${grouping}&average_window=${smoothing}`
  );
  const data = (await response.json()) as GraphData;
  return data;
}

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

export function ResultViewer(props: ResultViewerProps) {
  const graphState = useContext(GraphPageStateContext);
  const graphStateDispatch = useContext(GraphPageDispatchContext);
  if (!graphState || !graphStateDispatch)
    throw new Error("Graph state not initialized");
  const selectedPoint = React.useRef<Highcharts.Point>();
  const {
    selectedTicket,
    grouping,
    smoothing,
    tickets,
    month,
    contextYearRange: yearRange,
  } = graphState;
  const { lang } = useContext(LangContext);
  const translation = strings[lang];

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

  function setYearRange(yearRange: [number | undefined, number | undefined]) {
    graphStateDispatch!({
      type: "set_context_range",
      payload: yearRange,
    });
  }

  if (
    tickets &&
    tickets.length > 0 &&
    !tickets.some((t) => t.id === selectedTicket)
  ) {
    setSelectedTicket(tickets[0].id);
    setMonth(undefined);
    setYearRange([undefined, undefined]);
  }

  const ticketData = useQueries({
    queries:
      tickets?.map((ticket) => {
        const { id } = ticket;
        return {
          queryKey: ["ticket", { id, grouping, smoothing }],
          queryFn: () =>
            getTicketData(
              ticket.id,
              ticket.backend_source,
              grouping,
              smoothing
            ),
          keepPreviousData: true,
          refetchOnWindowFocus: false,
          initialData: props.initGraphData,
        };
      }) ?? [],
  });

  function handleSeriesClick(point: Highcharts.Point) {
    if (!graphStateDispatch) return;
    setSelectedTicket(
      tickets?.filter((t) => t.terms[0] === point.series.name)[0].id
    );
    const date = new Date(point.category);
    if (grouping === "year") {
      setMonth(undefined);
      setYearRange([date.getUTCFullYear(), date.getUTCFullYear() + 1]);
    } else {
      setMonth(date.getUTCMonth() + 1);
      setYearRange([date.getUTCFullYear(), date.getUTCFullYear() + 1]);
    }
  }

  function handleSetExtremes(e: Highcharts.AxisSetExtremesEventObject) {
    if (!graphStateDispatch) return;
    if (e.trigger === "zoom") {
      const minDate = new Date(e.min);
      const maxDate = new Date(e.max);
      if (minDate.toString() === "Invalid Date") {
        setMonth(undefined);
        setYearRange([undefined, undefined]);
        return;
      }
      if (grouping === "year") {
        setYearRange([minDate.getUTCFullYear(), maxDate.getUTCFullYear()]);
      } else {
        setYearRange([minDate.getUTCFullYear(), maxDate.getUTCFullYear()]);
        setMonth(minDate.getUTCMonth() + 1);
      }
    }
  }

  const highchartsOpts = makeOptions(
    handleSetExtremes,
    handleSeriesClick,
    ticketData
  );

  return (
    <div className={"h-full w-full bg-white"}>
      <div className={"relative"}>
        <div
          className={
            "ml-10 absolute -top-10 right-2 z-40 mb-5 flex flex-row gap-10"
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
              options={["0", "1", "2", "3", "4", "5", "10", "20", "50"]}
              onChange={(value: string) => setSmoothing(parseInt(value))}
              value={smoothing.toString()}
            />
          </InputLabel>
        </div>
        <HighchartsReact highcharts={Highcharts} options={highchartsOpts} />
      </div>
      <div className={"flex flex-col gap-5 ml-5 mr-5 mt-2"}>
        {translation.gallicagram_plug}
        <div className={"flex wrap gap-10"}>
          <SelectInput
            options={tickets?.map((ticket) => ticket.terms[0]) ?? []}
            onChange={(value: string) =>
              setSelectedTicket(
                tickets?.filter((t) => t.terms[0] === value)[0].id
              )
            }
            value={
              tickets?.filter((t) => t.id === selectedTicket)?.[0]?.terms[0]
            }
          />
          <ActiveFilters
            filters={[
              {
                label:
                  yearRange[0] && yearRange[1]
                    ? `${yearRange[0]} - ${yearRange[1]}`
                    : undefined,
                onClick: () => setYearRange([undefined, undefined]),
              },
              {
                label: month ? translation.months[month - 1] : undefined,
                onClick: () => setMonth(undefined),
              },
            ]}
          />
        </div>
      </div>
      <TicketResultTable
        initialRecords={props.initRecords}
        tickets={tickets}
        month={month}
        yearRange={yearRange}
        onSelectYear={(year) => setYearRange([year, undefined])}
        onSelectMonth={(month) => setMonth(month)}
        onSelectTicket={(ticket) => setSelectedTicket(ticket)}
        selectedTicket={selectedTicket}
        limit={10}
      />
    </div>
  );
}

function ActiveFilters(props: {
  filters: { label: any; onClick: () => void }[];
}) {
  return (
    <div className={"flex flex-row gap-2"}>
      {props.filters.map((filter) => {
        if (filter.label) {
          return (
            <button
              className={
                "flex flex-row gap-5 items-center border shadow-md rounded-md p-3 hover:bg-zinc-100"
              }
              key={filter.label}
              onClick={filter.onClick}
            >
              <div>{filter.label}</div>
              <div>X</div>
            </button>
          );
        }
      })}
    </div>
  );
}

function FrequencyContext(props: {
  yearRange: [number | undefined, number | undefined];
  month?: number;
  term?: string;
}) {
  async function getFrequencyData(
    yearRange: [number | undefined, number | undefined],
    month?: number,
    term?: string
  ) {
    const [start, end] = yearRange;
    const url = addQueryParamsIfExist(`${apiURL}/api/mostFrequentTerms`, {
      start_year: start,
      start_month: month,
      end_year: end,
      end_month: month,
      root_gram: term,
      sample_size: 30,
    });
    console.log(url);
    const response = await fetch(url);
    return (await response.json()) as FrequentTerm[];
  }

  const { data, isFetching } = useQuery(
    ["frequency", props.yearRange, props.month, props.term],
    () => getFrequencyData(props.yearRange, props.month, props.term)
  );

  if (isFetching) return <div>Loading...</div>;
  if (!data) return <div>No data</div>;
  return (
    <div className={"flex gap-10 flex-wrap"}>
      {data.map((term) => (
        <div className={"flex flex-col gap-2"} key={term.term}>
          <div className={"text-xl"}>{term.term}</div>
          <div className={"text-sm"}>{term.count}</div>
        </div>
      ))}
    </div>
  );
}
