import React from "react";
import { Ticket } from "../pages/index";
import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  Legend,
  Tooltip,
} from "recharts";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { generateXAxisOptionsForNumericScale } from "./utils";
import { useQueries, useQueryClient } from "@tanstack/react-query";
import { TicketResultTable } from "./TicketResultTable";
import { apiURL } from "./apiURL";
import { GraphData } from "../models/dbStructs";

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
}

export const ResultViewer: React.FC<ResultViewerProps> = (props) => {
  const [selectedYear, setSelectedYear] = React.useState<number>();
  const [selectedMonth, setSelectedMonth] = React.useState<number>();
  const [selectedDay, setSelectedDay] = React.useState<number>();
  const [selectedGrouping, setSelectedGrouping] = React.useState<
    "year" | "month"
  >("year");
  const [selectedSmoothing, setSelectedSmoothing] = React.useState<number>(0);

  async function getTicketData(
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
      };
    }),
  });

  const allDateMarksInTicketData = ticketData?.map((ticket) =>
    ticket.data?.data.map((data) => data.date)
  );

  //collapse array of arrays into one array
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

  return (
    <div className={"h-full w-full bg-white"}>
      <div className={"m-5 flex flex-row gap-10"}>
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
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          width={500}
          height={300}
          onClick={(e) => {
            if (!e) {
              return;
            }
            if (e.activePayload && e.activePayload.length > 0) {
              const payload = e.activePayload[0];
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
            domain={xAxisOptions.domain}
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
              animateNewValues={false}
              data={ticket.data?.data}
              name={ticket.data?.name}
              dot={false}
              key={index}
              style={{ cursor: "pointer" }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <TicketResultTable
        tickets={props.tickets}
        month={selectedMonth}
        day={selectedDay}
        year={selectedYear}
        onSelectYear={(year) => setSelectedYear(year)}
        onSelectMonth={(month) => setSelectedMonth(month)}
        onSelectDay={(day) => setSelectedDay(day)}
      />
    </div>
  );
};