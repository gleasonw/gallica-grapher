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
  {
    id: 1,
    terms: ["congo"],
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
  initSeries: GraphData[];
}> = async () => {
  const records = await fetchContext(
    { pageParam: 0 },
    {
      terms: initTickets[0].terms[0],
      limit: 10,
      source: "periodical",
    }
  );
  const initSeries = await Promise.all(
    initTickets.map((ticket) => {
      return getTicketData(
        ticket.id,
        ticket.backend_source,
        ticket.grouping,
        0
      );
    })
  );
  return {
    props: {
      // @ts-ignore
      initRecords: records,
      initSeries: initSeries,
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
        onDeleteExampleTickets={() => {
          setTickets(tickets.filter((t) => !t.example));
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
