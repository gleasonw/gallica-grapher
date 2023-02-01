import { Inter } from "@next/font/google";
import React, { useState } from "react";
import { BaseLayout } from "../components/BaseLayout";
import { InputForm } from "../components/InputForm";
import { ResultViewer, getTicketData } from "../components/ResultViewer";
import { GallicaResponse, GraphData, Paper } from "../models/dbStructs";
import { GetStaticProps, InferGetStaticPropsType } from "next/types";
import { fetchContext } from "../components/ResultsTable";

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
  link_term?: string;
  link_distance?: number;
  example?: boolean;
}

export const initTickets = [
  {
    id: 0,
    terms: ["brazza"],
    grouping: "month",
    example: true,
  },
] as Ticket[];

export const getStaticProps: GetStaticProps<{
  initRecords: {
    data: GallicaResponse;
    nextCursor: number | null;
    previousCursor: number;
  };
  initSeries: GraphData;
}> = async () => {
  const initTicket = initTickets[0];
  const records = fetchContext(
    { pageParam: 0 },
    {
      terms: initTicket.terms[0],
      limit: 10,
    }
  );
  const series = getTicketData(
    initTicket.id,
    "pyllica",
    "year",
    0
  );
  const data = await Promise.allSettled([records, series]);
  return {
    props: {
      // @ts-ignore
      initRecords: data[0].value,
      // @ts-ignore
      initSeries: data[1].value,
    },
  };
};

export default function Home({
  initRecords,
  initSeries,
}: InferGetStaticPropsType<typeof getStaticProps>) {
  const [tickets, setTickets] = useState<Ticket[]>(initTickets);
  const [outerRange, setOuterRange] = useState<[number, number]>([1789, 2000]);

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
      <ResultViewer
        tickets={tickets}
        outerRange={outerRange}
        initVals={{ initRecords, initSeries }}
      />
    </BaseLayout>
  );
}
