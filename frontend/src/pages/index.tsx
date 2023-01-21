import { Inter } from "@next/font/google";
import React, { useState } from "react";
import { Paper } from "../server/routers/_app";
import { BaseLayout } from "../components/BaseLayout";
import { InputForm } from "../components/InputForm";
import { ResultViewer } from "../components/ResultViewer";
import { createProxySSGHelpers } from "@trpc/react-query/ssg";
import { appRouter } from "../server/routers/_app";
import { trpc } from "../utils/trpc";
import { tickStep } from "d3";

const inter = Inter({ subsets: ["latin"] });

export type changeHandler = (e: React.ChangeEvent<HTMLInputElement>) => void;

export interface Ticket {
  id: number;
  terms: string[];
  grouping: "month";
  backend_source?: "gallica" | "pyllica";
  start_date?: number;
  end_date?: number;
  papers?: Paper[];
  num_results?: number;
  start_index?: number;
  num_workers?: number;
  link_term?: string;
  link_distance?: number;
}

const initTickets = [
  {
    id: 0,
    terms: ["brazza"],
    grouping: "month",
  },
  {
    id: 1,
    terms: ["congo"],
    grouping: "month",
  },
  {
    id: 2,
    terms: ["stanley"],
    grouping: "month",
  },
] as Ticket[];

export async function getStaticProps() {
  const ssg = createProxySSGHelpers({
    router: appRouter,
    ctx: {},
  });

  initTickets.map(async (ticket) => {
    console.log("fetch server side")
    await ssg.graphData.fetch({
      id: ticket.id,
      grouping: "month",
      smoothing: 0,
      backend_source: "pyllica",
    });
  });

  await ssg.gallicaRecords.fetch({
    terms: initTickets[0].terms,
  });

  return {
    props: {
      trpcState: ssg.dehydrate(),
    },
  };
}

export default function Home() {
  const [tickets, setTickets] = useState<Ticket[]>(initTickets);
  const [outerRange, setOuterRange] = useState<[number, number]>([1865, 1950]);

  return (
    <BaseLayout>
      <InputForm
        onCreateTicket={(ticket: Ticket) => {
          if (tickets) {
            setTickets([...tickets, ticket]);
          } else {
            setTickets([ticket]);
          }
        }}
        onSliderChange={(range: [number, number]) => {
          setOuterRange(range);
        }}
        tickets={tickets}
        yearRange={outerRange}
        onDeleteTicket={(ticket?: Ticket) => {
          if (tickets && ticket) {
            setTickets(tickets.filter((t) => t.id !== ticket.id));
          }
        }}
      />
      <ResultViewer tickets={tickets} outerRange={outerRange} />
    </BaseLayout>
  );
}
