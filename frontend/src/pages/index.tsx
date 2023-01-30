import { Inter } from "@next/font/google";
import React, { useState } from "react";
import { Paper } from "../server/routers/_app";
import { BaseLayout } from "../components/BaseLayout";
import { InputForm } from "../components/InputForm";
import { ResultViewer } from "../components/ResultViewer";
import { createProxySSGHelpers } from "@trpc/react-query/ssg";
import { appRouter } from "../server/routers/_app";
import {
  DehydratedState,
  hydrate,
  useHydrate,
  useQueryClient,
} from "@tanstack/react-query";
import { GetStaticProps, InferGetStaticPropsType } from "next/types";

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
] as Ticket[];

export const getStaticProps: GetStaticProps<{
  trpcState: DehydratedState;
}> = async () => {
  const ssg = createProxySSGHelpers({
    router: appRouter,
    ctx: {},
  });

  await Promise.allSettled([
    ssg.graphData.prefetch({
      id: initTickets[0].id,
      grouping: "year",
      smoothing: 0,
      backend_source: "pyllica",
    }),
    ssg.gallicaRecords.prefetch({
      terms: initTickets[0].terms[0],
      codes: [],
      limit: 20,
    }),
  ]);

  return {
    props: {
      trpcState: ssg.dehydrate(),
    },
  };
};

export default function Home({
  trpcState,
}: InferGetStaticPropsType<typeof getStaticProps>) {
  const [tickets, setTickets] = useState<Ticket[]>(initTickets);
  const [outerRange, setOuterRange] = useState<[number, number]>([1789, 2000]);
  useHydrate(trpcState);

  return (
    <BaseLayout>
      <div className="m-10 text-center text-4xl">
        {" "}
        View word occurrences in archived French periodicals.
      </div>
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
