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
import { TermSearchInput, YearInput } from "@/src/app/terms-search";
import { GallicaGramChart } from "@/src/app/gallicagram-chart";
import { $path, InferPagePropsType } from "next-typesafe-url";
import { withParamValidation } from "next-typesafe-url/app/hoc";
import { type RouteType, Route, SearchParams } from "@/src/app/routeType";
import { SkeletonsWhenLoading } from "@/src/app/SkeletonsWhenLoading";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
} from "@/components/ui/pagination";
import { NumberRecords } from "@/src/app/NumberRecords";

import Link from "next/link";
import React from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft, Copy, Image } from "lucide-react";
import {
  RecordContextProvider,
  RecordContextNavigator,
  RecordContextPageSelect,
} from "@/src/app/RecordContext";

type PageProps = InferPagePropsType<RouteType>;

const frenchAnimals = [
  "chien", // dog
  "chat", // cat
  "lapin", // rabbit
  "cheval", // horse
  "vache", // cow
  "mouton", // sheep
  "cochon", // pig
  "poule", // hen
  "canard", // duck
  "oiseau", // bird
  "poisson", // fish
  "serpent", // snake
  "grenouille", // frog
  "souris", // mouse
  "chèvre", // goat
  "renard", // fox
  "singe", // monkey
  "ours", // bear
  "tigre", // tiger
  "éléphant", // elephant
  "girafe", // giraffe
  "lion", // lion
  "zèbre", // zebra
  "hippopotame", // hippopotamus
  "kangourou", // kangaroo
  "perroquet", // parrot
  "panda", // panda
  "léopard", // leopard
  "pingouin", // penguin
  "hirondelle", // swallow
];

// TODO:

// errors screen for gallica
// french translation
// click on chart to go to year

function TestScroll() {
  return (
    <div className="flex flex-col gap-2 max-h-[100px] overflow-auto">
      {frenchAnimals.map((a) => (
        <Link href={$path({ route: "/", searchParams: { terms: [a] } })}>
          {a}
        </Link>
      ))}
    </div>
  );
}

async function GallicaGrapher({ searchParams }: PageProps) {
  return (
    <div className="flex flex-col">
      <header className="px-6 py-4 flex flex-col">
        <div className="flex items-center space-x-2">
          <div className="relative flex-grow">
            <TermSearchInput />
          </div>
          <Filters />
        </div>
      </header>
      <main className="flex-1 p-6">
        <div className="w-full h-32">
          <Suspense key={JSON.stringify(searchParams.terms)}>
            <ChartFetch terms={searchParams.terms} />
          </Suspense>
        </div>
        <RecordsScroll searchParams={searchParams} />

        <Suspense
          fallback={
            <RecordsLayout
              header={
                <div className="w-full h-[40px] bg-gray-200 animate-pulse rounded-md" />
              }
              records={Array.from({ length: 5 }).map(() => (
                <div className="h-44 w-full animate-pulse bg-gray-200 rounded-md"></div>
              ))}
            />
          }
          key={JSON.stringify({
            ...searchParams,
            ark_selected_page: undefined,
            ark_show_image: undefined,
          })}
        ></Suspense>
      </main>
    </div>
  );
}

export default withParamValidation(GallicaGrapher, Route);

const client = createClient<paths>({
  baseUrl:
    process.env.NODE_ENV === "development"
      ? "http://localhost:8000"
      : "https://gallica-proxy-production.up.railway.app",
});

async function ChartFetch({ terms }: { terms: string[] }) {
  const { data, error } = await client.GET("/api/series", {
    params: { query: { term: terms[0] ?? "brazza", grouping: "annee" } },
  });

  if (error) {
    return <div>Error: {error.detail?.[0]?.msg}</div>;
  }

  return <GallicaGramChart series={data} />;
}

function RecordsLayout({
  records,
  header,
}: {
  records: React.ReactNode;
  header: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4 justify-between">{header}</div>
      <ScrollArea className="h-[900px] max-h-screen rounded-md">
        <div className="gap-4 grid grid-cols-1 ">{records}</div>
      </ScrollArea>
    </div>
  );
}

async function RecordsScroll({ searchParams }: { searchParams: SearchParams }) {
  const { data, error } = await client.GET("/api/occurrences_no_context", {
    params: { query: searchParams },
  });

  if (error) {
    return <div>Error: {error.detail?.[0]?.msg}</div>;
  }

  const numPages = Math.ceil(data?.total_records / (searchParams?.limit ?? 10));
  const currentPage = Math.floor((searchParams?.cursor ?? 0) / 10) + 1;
  const pagesBeforeToDisplay = Math.min(2, currentPage - 1);
  const pagesAfterToDisplay = Math.min(2, numPages - currentPage);

  return (
    <RecordsLayout
      header={
        <>
          <span className="text-nowrap font-bold text-2xl">
            <NumberRecords records={data?.total_records} />
          </span>
          <Pagination>
            <PaginationContent>
              <Button variant="ghost" disabled={currentPage === 1}>
                <Link
                  className="flex gap-2 items-center"
                  href={$path({
                    route: "/",
                    searchParams: {
                      ...searchParams,
                      cursor: (currentPage - 1) * 10 - 10,
                    },
                  })}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Link>
              </Button>

              {Array.from({ length: pagesBeforeToDisplay }).map((_, i) => (
                <PaginationItem key={i}>
                  <PaginationLink
                    href={$path({
                      route: "/",
                      searchParams: {
                        ...searchParams,
                        cursor:
                          (currentPage - 1) * 10 -
                          (pagesBeforeToDisplay - i) * 10,
                      },
                    })}
                  >
                    {currentPage - pagesBeforeToDisplay + i}
                  </PaginationLink>
                </PaginationItem>
              ))}

              <PaginationItem>
                <PaginationLink
                  isActive={true}
                  href={$path({ route: "/", searchParams })}
                >
                  {currentPage}
                </PaginationLink>
              </PaginationItem>

              {Array.from({ length: pagesAfterToDisplay }).map((_, i) => (
                <PaginationItem key={i}>
                  <PaginationLink
                    href={$path({
                      route: "/",
                      searchParams: {
                        ...searchParams,
                        cursor: (currentPage - 1) * 10 + (i + 1) * 10,
                      },
                    })}
                  >
                    {currentPage + (i + 1)}
                  </PaginationLink>
                </PaginationItem>
              ))}

              <Button variant="ghost" disabled={currentPage === numPages}>
                <PaginationNext
                  href={$path({
                    route: "/",
                    searchParams: {
                      ...searchParams,
                      cursor: (currentPage - 1) * 10 + 10,
                    },
                  })}
                />
              </Button>
            </PaginationContent>
          </Pagination>
          <YearInput params={searchParams} />
        </>
      }
      records={
        <SkeletonsWhenLoading
          loadedUI={data.records.map((record) => (
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
                    <VolumeRecordOccurrences
                      record={record}
                      params={searchParams}
                    />
                  </Suspense>
                </CardContent>
              </Card>
            </ImageStateProvider>
          ))}
        />
      }
    />
  );
}

async function VolumeRecordOccurrences({
  record,
  params,
}: {
  record: VolumeRecord;
  params: SearchParams;
}) {
  const { data, error } = await client.GET("/api/context", {
    params: {
      query: { ark: record.ark, terms: record.terms, url: record.url },
    },
  });

  const selectedPageNumber = params?.ark_selected_page?.[record.ark];

  if (error) {
    return <div>Error: {error.detail?.[0]?.msg}</div>;
  }

  const pageNumbers = data?.map((page) => page.page_num);

  const uniqueFiltered = Array.from(new Set(pageNumbers))
    .filter((p) => p !== undefined)
    .sort((a, b) => {
      if (a === undefined || b === undefined) {
        return 0;
      }
      return a - b;
    });

  const selectedPage =
    uniqueFiltered.find((p) => p === selectedPageNumber) ??
    uniqueFiltered.at(0);

  if (!selectedPage) {
    return <div>Logic error trying to find selected page number.</div>;
  }

  const showImage = params?.ark_show_image?.[record.ark] ?? false;

  const imageData = showImage
    ? await client.GET("/api/image", {
        params: {
          query: {
            ark: record.ark,
            page: selectedPage,
            term: record.terms[0]!,
          },
        },
      })
    : null;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-col gap-4">
        {data.map((c, index) => (
          <span
            key={`${c.left_context}${c.page_num}${c.right_context}${index}`}
          >
            {c.left_context}{" "}
            <span className={" font-bold px-8 bg-yellow-300"}>{c.pivot}</span>{" "}
            {c.right_context}
          </span>
        ))}
      </div>
      <div className="flex gap-2 items-center">
        <Link
          className="ml-auto"
          href={$path({
            route: "/",
            searchParams: {
              ...params,
              ark_show_image: {
                ...params?.ark_show_image,
                [record.ark]: true,
              },
            },
          })}
        >
          <Button variant="outline">
            <Image />
          </Button>
        </Link>

        <Button variant="outline">
          <Copy />
        </Button>
      </div>
      <RecordContextNavigator context={data} />
      {imageData ? (
        <img
          src={imageData?.data?.image}
          alt={`Page of text occurrences from Gallica`}
        />
      ) : null}
    </div>
  );
}
