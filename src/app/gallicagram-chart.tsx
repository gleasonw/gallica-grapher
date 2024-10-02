"use client";
import { Series } from "@/src/app/types";
import { useMemo } from "react";
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Bar,
  BarChart,
} from "recharts";
import { firstBy } from "remeda";

// TODO: fix weird buckets coming from shiny api proxy

export function GallicaGramChart({ series }: { series: Series }) {
  const minX = firstBy(series.data, (d) => d[0]);
  const maxX = firstBy(series.data, [(d) => d[0], "desc"]);
  if (!minX || !maxX) {
    console.error("No data");
    return null;
  }
  const domain = [minX[0], maxX[0]];
  const dataInRechartsFormat = useMemo(() => {
    return series.data.map((d) => ({
      timeEpochSeconds: d[0],
      frequency: d[1],
    }));
  }, [series.data]);
  return (
    <ResponsiveContainer width="100%" height="90%">
      <BarChart
        data={dataInRechartsFormat}
        onClick={(data) => console.log(data)}
      >
        <CartesianGrid />
        <XAxis
          domain={domain}
          dataKey="timeEpochSeconds"
          tickFormatter={(value) => new Date(value).getFullYear().toString()}
          tickCount={5}
        />
        <YAxis />
        <Tooltip
          labelFormatter={(epochSeconds) =>
            new Date(epochSeconds).toLocaleDateString()
          }
        />
        <Bar type="monotone" dataKey="frequency" stroke="#8884d8" />
      </BarChart>
    </ResponsiveContainer>
  );
}
