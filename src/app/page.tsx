import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import createClient from "openapi-fetch";
import "@/src/globals.css";

import { Filters } from "@/src/app/filters";
import { VolumeRecord } from "@/src/app/types";
import { paths } from "@/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Suspense } from "react";
import { ImageStateProvider } from "@/src/app/client-state-providers";
import { TermSearchInput } from "@/src/app/terms-search";
import { GallicaGramChart } from "@/src/app/gallicagram-chart";
import { $path } from "next-typesafe-url";
import Link from "next/link";

export default async function GallicaGrapher({
  searchParams,
}: {
  searchParams: Record<string, string>;
}) {
  const term = searchParams.term ?? "brazza";
  return (
    <div className="flex flex-col">
      <header className="px-6 py-4 flex flex-col">
        <div className="flex items-center space-x-2">
          <div className="relative flex-grow">
            <TermSearchInput />
          </div>
          <Button size="lg" className="px-8 shadow-lg">
            Search
          </Button>
          <Filters />
          <Link
            href={$path({
              route: "/",
            })}
          >
            this is a test
          </Link>
          ;
        </div>
      </header>
      <main className="flex-1 p-6">
        <div className="w-full h-32">
          <Suspense fallback={<div>Loading chart...</div>}>
            <ChartFetch term={term} />
          </Suspense>
        </div>
        <Suspense fallback={<div>Loading hits...</div>}>
          <RecordsScroll term={term} />
        </Suspense>
      </main>
    </div>
  );
}

const client = createClient<paths>({
  baseUrl:
    process.env.NODE_ENV === "development"
      ? "http://localhost:8000"
      : "https://gallica-proxy-production.up.railway.app",
});

async function ChartFetch({ term }: { term: string }) {
  const { data, error } = await client.GET("/api/series", {
    params: { query: { term, grouping: "annee" } },
  });

  if (error) {
    return <div>Error: {error.detail?.[0]?.msg}</div>;
  }

  return <GallicaGramChart series={data} />;
}

async function RecordsScroll({ term }: { term: string }) {
  const { data, error } = await client.GET("/api/occurrences_no_context", {
    params: { query: { terms: [term] } },
  });

  if (error) {
    return <div>Error: {error.detail?.[0]?.msg}</div>;
  }

  return (
    <ScrollArea className="h-[900px] max-h-screen rounded-md">
      <div className="gap-4 grid grid-cols-1 sm:grid-cols-2">
        {data.records.map((record) => (
          <ImageStateProvider>
            <Card className="h-full">
              <CardHeader className="">
                <CardTitle className="text-sm font-medium">
                  {record.paper_title}
                </CardTitle>
                <CardDescription>{record.date}</CardDescription>
              </CardHeader>
              <CardContent>
                <Suspense fallback={<div>Loading context...</div>}>
                  <VolumeRecordOccurrences record={record} />
                </Suspense>
              </CardContent>
            </Card>
          </ImageStateProvider>
        ))}
      </div>
    </ScrollArea>
  );
}

async function VolumeRecordOccurrences({ record }: { record: VolumeRecord }) {
  const { data, error } = await client.GET("/api/context", {
    params: {
      query: { ark: record.ark, terms: record.terms, url: record.url },
    },
  });

  if (error) {
    return <div>Error: {error.detail?.[0]?.msg}</div>;
  }

  return data?.slice(0, 1).map((row) => (
    <div className="">
      {row.left_context} <span className="bg-yellow-500 px-5">{row.pivot}</span>{" "}
      {row.right_context}
    </div>
  ));
}
