import React, { useEffect, useRef } from "react";
import { trpc } from "../utils/trpc";
import { Ticket } from "../pages/index";
import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  Legend,
  Tooltip,
} from "recharts";
import { ResultsTable } from "./ResultsTable";
import { InputLabel } from "./InputLabel";
import { SelectInput } from "./SelectInput";
import { generateXAxisOptionsForNumericScale } from "./utils";
import { DehydratedState } from "@tanstack/react-query";

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
  initialData: DehydratedState
}

export const ResultViewer: React.FC<ResultViewerProps> = (props) => {
  const [selectedYear, setSelectedYear] = React.useState<number>();
  const [selectedMonth, setSelectedMonth] = React.useState<number>();
  const [selectedDay, setSelectedDay] = React.useState<number>();
  const [selectedGrouping, setSelectedGrouping] = React.useState<
    "year" | "month"
  >("year");
  const [selectedSmoothing, setSelectedSmoothing] = React.useState<number>(0);

  const ticketData = trpc.useQueries((query) =>
    props.tickets.map((ticket) =>
      query.graphData(
        {
          id: ticket.id,
          backend_source: ticket.backend_source || "pyllica",
          grouping: selectedGrouping,
          smoothing: selectedSmoothing,
        },
        { keepPreviousData: true }
      )
    )
  );

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
    <div className={"w-full h-full bg-white"}>
      <div className={"flex flex-row gap-10 m-5"}>
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
              data={ticket.data?.data}
              name={ticket.data?.name}
              dot={false}
              key={index}
              style={{ cursor: "pointer" }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <ResultsTable
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
