import React, { useEffect } from "react";
import { Ticket, getStaticProps } from "../pages/index";
import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  Legend,
  Tooltip,
  ReferenceArea,
} from "recharts";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { generateXAxisOptionsForNumericScale } from "./utils";
import { useQueries, useQueryClient } from "@tanstack/react-query";
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

export function ResultViewer(props: ResultViewerProps) {
  const [selectedTicket, setSelectedTicket] = React.useState<Ticket | null>(
    props.tickets && props.tickets.length > 0 ? props.tickets[0] : null
  );
  const [selectedYear, setSelectedYear] = React.useState<number | null>(null);
  const [selectedMonth, setSelectedMonth] = React.useState<number | null>(null);
  const [selectedDay, setSelectedDay] = React.useState<number | null>(null);
  const [selectedGrouping, setSelectedGrouping] = React.useState<
    "year" | "month"
  >("year");
  const [selectedSmoothing, setSelectedSmoothing] = React.useState<number>(0);

  //zoom state
  const [zoomed, setZoomed] = React.useState<boolean>(false);
  const [refAreaLeft, setRefAreaLeft] = React.useState<number | null>(null);
  const [refAreaRight, setRefAreaRight] = React.useState<number | null>(null);
  const [dataMin, setDataMin] = React.useState<number | null>(null);
  const [dataMax, setDataMax] = React.useState<number | null>(null);

  React.useEffect(() => {
    if (
      props.tickets.length > 0 &&
      !props.tickets.some((t) => t.id === selectedTicket?.id)
    ) {
      setSelectedTicket(props.tickets[0]);
      setSelectedDay(null);
      setSelectedMonth(null);
      setSelectedYear(null);
    }
  }, [props.tickets, selectedTicket]);

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

  const allDateMarksInTicketData = ticketData?.map((ticket) =>
    ticket.data?.data.map((data) => data.date)
  );

  const allDateMarks = allDateMarksInTicketData?.reduce((acc, val) => {
    if (val && acc) {
      return acc.concat(val);
    } else {
      return acc;
    }
  }, []);

  const monthNames = [
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
  ];

  const xAxisOptions = generateXAxisOptionsForNumericScale(allDateMarks || []);

  function formatTicks(tick: string): string {
    if (selectedGrouping === "year") {
      return tick;
    } else {
      const date = new Date(parseInt(tick));
      return `${monthNames[date.getMonth()]} ${date.getFullYear()}`;
    }
  }

  function zoom() {
    if (refAreaLeft === refAreaRight || refAreaRight === null) {
      setZoomed(false);
    } else {
      setZoomed(true);
      //ensure that dataMin is always less than dataMax
      if (refAreaLeft && refAreaLeft < refAreaRight) {
        setDataMin(refAreaLeft);
        setDataMax(refAreaRight);
      } else {
        setDataMin(refAreaRight);
        setDataMax(refAreaLeft);
      }
    }
    setRefAreaLeft(null);
    setRefAreaRight(null);
  }

  function zoomOut() {
    setZoomed(false);
    setDataMax(null);
    setDataMin(null);
  }

  function determineXDomain() {
    if (dataMin && dataMax) {
      return [dataMin, dataMax];
    } else {
      return [xAxisOptions.domain[0], xAxisOptions.domain[1]];
    }
  }

  console.log(refAreaLeft, refAreaRight);
  return (
    <div className={"h-full w-full bg-white"}>
      <div className={"ml-10 mb-5 flex flex-row gap-10"}>
        <InputLabel label={"Grouping"}>
          <SelectInput
            options={["year", "month"]}
            onChange={(value: string) =>
              setSelectedGrouping(value as "year" | "month")
            }
            value={selectedGrouping}
          />
        </InputLabel>
        <InputLabel label={"Smoothing"}>
          <SelectInput
            options={["0", "1", "2", "3", "4", "5", "10", "20", "50"]}
            onChange={(value: string) => setSelectedSmoothing(parseInt(value))}
            value={selectedSmoothing.toString()}
          />
        </InputLabel>
      </div>
      {zoomed && (
        <button
          onClick={zoomOut}
          className={" rounded-sm border p-5 hover:bg-zinc-100"}
        >
          Zoom out
        </button>
      )}
      <ResponsiveContainer width="100%" height={400} className={"mb-10"}>
        <LineChart
          width={500}
          height={300}
          onMouseDown={(e: any) => {
            if (e && e.activeLabel) {
              setRefAreaLeft(e.activeLabel);
            }
          }}
          onMouseMove={(e: any) => {
            if (refAreaLeft && e.activeLabel) {
              setRefAreaRight(e.activeLabel);
            }
          }}
          onMouseUp={zoom}
          onClick={(e) => {
            if (!e) {
              return;
            }
            if (e.activePayload && e.activePayload.length > 0) {
              const payload = e.activePayload[0];
              console.log(payload.name);
              if (payload.payload && payload.payload.date) {
                if (selectedGrouping === "year") {
                  setSelectedYear(parseInt(payload.payload.date));
                } else {
                  const date = new Date(parseInt(payload.payload.date));
                  setSelectedMonth(date.getMonth() + 1);
                  setSelectedYear(date.getFullYear());
                }
              }
            }
          }}
          // @ts-ignore
          cursor={"pointer"}
        >
          <XAxis
            dataKey={"date"}
            domain={determineXDomain}
            scale={xAxisOptions.scale}
            type={xAxisOptions.type}
            ticks={xAxisOptions.ticks}
            allowDuplicatedCategory={false}
            tickFormatter={formatTicks}
          />
          <Legend />
          <Tooltip labelFormatter={(label) => formatTicks(label as string)} />
          {ticketData.map((ticket, index) => (
            <Line
              type="monotone"
              dataKey="count"
              stroke={seriesColors[index % seriesColors.length]}
              strokeWidth={2}
              data={ticket.data?.data}
              name={ticket.data?.name}
              dot={false}
              key={index}
              style={{ cursor: "pointer" }}
            />
          ))}
          {refAreaLeft && refAreaRight ? (
            <ReferenceArea
              x1={refAreaLeft}
              x2={refAreaRight}
              strokeOpacity={0.3}
            />
          ) : null}
        </LineChart>
      </ResponsiveContainer>
      <TicketResultTable
        initialRecords={props.initVals.initRecords}
        tickets={props.tickets}
        month={selectedMonth}
        day={selectedDay}
        year={selectedYear}
        onSelectYear={(year) => setSelectedYear(year)}
        onSelectMonth={(month) => setSelectedMonth(month)}
        onSelectDay={(day) => setSelectedDay(day)}
        onSelectTicket={(ticket) => setSelectedTicket(ticket)}
        selectedTicket={selectedTicket}
        limit={10}
      />
    </div>
  );
}
