"use client";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { year: "1900", count: 5 },
  { year: "1910", count: 8 },
  { year: "1920", count: 15 },
  { year: "1930", count: 22 },
  { year: "1940", count: 30 },
  { year: "1950", count: 45 },
  { year: "1960", count: 60 },
  { year: "1970", count: 75 },
  { year: "1980", count: 90 },
  { year: "1990", count: 120 },
  { year: "2000", count: 150 },
];

export function GallicaGramChart() {
  return (
    <ResponsiveContainer width="100%" height="90%">
      <LineChart data={data} onClick={(data) => console.log(data)}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="year" />
        <YAxis />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="count"
          stroke="#8884d8"
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
