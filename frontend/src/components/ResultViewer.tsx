import React, { useContext } from "react";
import { LangContext } from "../pages";
import { Ticket, getStaticProps } from "../pages/index";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { useQueries } from "@tanstack/react-query";
import { TicketResultTable } from "./TicketResultTable";
import { apiURL } from "./apiURL";
import { GraphData } from "../models/dbStructs";
import { InferGetStaticPropsType } from "next";

export const seriesColors = [
  "#7cb5ec",
  "#434348",
  "#90ed7d",
  "#f7a35c",
  "#8085e9",
  "#f15c80",
  "#e4d354",
  "#2b908f",
  "#f45b5b",
  "#91e8e1",
];

interface ResultViewerProps {
  tickets: Ticket[];
  outerRange: [number, number];
  initVals: InferGetStaticPropsType<typeof getStaticProps>;
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
  },
};

export function ResultViewer(props: ResultViewerProps) {
  const [selectedTicket, setSelectedTicket] = React.useState<number | null>(
    null
  );
  const [selectedYear, setSelectedYear] = React.useState<number | null>(null);
  const [selectedMonth, setSelectedMonth] = React.useState<number | null>(null);
  const [selectedGrouping, setSelectedGrouping] = React.useState<
    "year" | "month"
  >("year");
  const [selectedSmoothing, setSelectedSmoothing] = React.useState<number>(0);

  const { lang } = useContext(LangContext);
  const translation = strings[lang];

  if (
    props.tickets.length > 0 &&
    !props.tickets.some((t) => t.id === selectedTicket)
  ) {
    setSelectedTicket(props.tickets[0].id);
    setSelectedMonth(null);
    setSelectedYear(null);
  }

  const ticketData = useQueries({
    queries: props.tickets.map((ticket) => {
      return {
        queryKey: ["ticket", ticket.id, selectedGrouping, selectedSmoothing],
        queryFn: () =>
          getTicketData(
            ticket.id,
            ticket.backend_source,
            selectedGrouping,
            selectedSmoothing
          ),
        staleTime: Infinity,
        placeholderData: props.initVals.initSeries.filter(
          (series) => series.request_id === ticket.id
        )[0],
        keepPreviousData: true,
      };
    }),
  });

  function handleSeriesClick(e: Highcharts.Point) {
    setSelectedTicket(
      props.tickets.filter((t) => t.terms[0] === e.series.name)[0].id
    );
    const date = new Date(e.category);
    if (selectedGrouping === "year") {
      setSelectedYear(date.getUTCFullYear());
      setSelectedMonth(0);
    } else {
      setSelectedYear(date.getUTCFullYear());
      setSelectedMonth(date.getUTCMonth() + 1);
    }
  }

  const getSeries = React.useCallback(
    () =>
      ticketData
        .filter((ticket) => ticket.data !== undefined)
        .map((ticket, i) => ({
          name: ticket.data!.name,
          data: ticket.data!.data,
          color: seriesColors[i],
        })),
    [ticketData]
  );

  const highchartsOpts: Highcharts.Options = {
    chart: {
      type: "line",
      zooming: {
        type: "x",
      },
    },
    title: {
      text: "",
    },
    xAxis: {
      type: "datetime",
    },
    yAxis: {
      title: {
        text: "Frequency",
      },
    },
    tooltip: {
      shared: true,
    },
    plotOptions: {
      series: {
        cursor: "pointer",
        events: {
          click: (e) => handleSeriesClick(e.point),
        },
        marker: {
          enabled: false,
          states: {
            hover: {
              enabled: true,
            },
            select: {
              enabled: true,
            },
          },
        },
      },
    },
    // @ts-ignore
    series: getSeries(),
  };

  return (
    <div className={"h-full w-full bg-white"}>
      <div className={"ml-10 mb-5 flex flex-row gap-10"}>
        <InputLabel label={translation.grouping}>
          <SelectInput
            options={["year", "month"]}
            onChange={(value: string) =>
              setSelectedGrouping(value as "year" | "month")
            }
            value={selectedGrouping}
          />
        </InputLabel>
        <InputLabel label={translation.smoothing}>
          <SelectInput
            options={["0", "1", "2", "3", "4", "5", "10", "20", "50"]}
            onChange={(value: string) => setSelectedSmoothing(parseInt(value))}
            value={selectedSmoothing.toString()}
          />
        </InputLabel>
      </div>
      <HighchartsReact highcharts={Highcharts} options={highchartsOpts} />
      <div className={"ml-5 mr-5 mt-2"}>{translation.gallicagram_plug}</div>
      <TicketResultTable
        initialRecords={props.initVals.initRecords}
        tickets={props.tickets}
        month={selectedMonth}
        year={selectedYear}
        onSelectYear={(year) => setSelectedYear(year)}
        onSelectMonth={(month) => setSelectedMonth(month)}
        onSelectTicket={(ticket) => setSelectedTicket(ticket)}
        selectedTicket={selectedTicket}
        limit={10}
      />
    </div>
  );
}
