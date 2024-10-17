import "@/src/globals.css";

import { Filters } from "@/src/app/filters";
import { Context, VolumeRecord } from "@/src/app/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Suspense } from "react";
import { TermSearchInput } from "@/src/app/terms-search";
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
import * as R from "remeda";

import Link from "next/link";
import React from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ExternalLink } from "lucide-react";
import {
  CopyButton,
  GrapherTooltip,
  PageImage,
  PageImageGate,
  ShowImageButton,
} from "@/src/app/GrapherTooltip";
import { PageContextClientStateProvider } from "@/src/app/PageContextClientStateProvider";
import { client } from "@/src/app/utils";

type PageProps = InferPagePropsType<RouteType>;

// Site en français

async function GallicaGrapher({ searchParams }: PageProps) {
  return (
    <div className="flex flex-col h-screen overflow-hidden px-2 pb-2 gap-4">
      <header className="py-4 flex flex-col gap-2">
        <div className="flex items-center space-x-2">
          <div className="relative flex-grow">
            <TermSearchInput />
          </div>
          <Filters />
        </div>
        <div className="ml-auto">
          <Feedback />
        </div>
      </header>
      <div className="w-full h-32 flex">
        <Suspense key={JSON.stringify(searchParams.terms)}>
          <ChartFetch terms={searchParams.terms} />
        </Suspense>
      </div>
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
          searchParams,
        })}
      >
        <RecordsScroll searchParams={searchParams} />
      </Suspense>
    </div>
  );
}

export default withParamValidation(GallicaGrapher, Route);

async function ChartFetch({ terms }: { terms: string[] }) {
  const { data, error } = await client.GET("/api/series", {
    params: { query: { term: terms[0] ?? "brazza", grouping: "annee" } },
  });

  if (error) {
    return <div>Erreur : {error.detail?.[0]?.msg}</div>;
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
    <div className="flex flex-col gap-5 pb-2 max-h-full h-full overflow-hidden">
      <div className="flex items-center gap-4 justify-between">{header}</div>
      <div className="gap-4 grid grid-cols-2 max-h-full overflow-auto p-0 ">
        {records}
      </div>
    </div>
  );
}

async function RecordsScroll({ searchParams }: { searchParams: SearchParams }) {
  const { data, error } = await client.GET("/api/occurrences_no_context", {
    params: { query: searchParams },
  });

  if (error) {
    return <div>Erreur : {error.detail?.[0]?.msg}</div>;
  }

  if (!data) {
    return <div>Pas de données</div>;
  }

  const numPages = Math.ceil(data?.total_records / (searchParams?.limit ?? 10));
  const currentPage = Math.floor((searchParams?.cursor ?? 0) / 10) + 1;
  const pagesBeforeToDisplay = Math.min(2, currentPage - 1);
  const pagesAfterToDisplay = Math.min(2, numPages - currentPage);

  return (
    <RecordsLayout
      header={
        <div className="w-full flex flex-col gap-3">
          <div className="flex gap-2 items-center justify-between w-full">
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
                    Précédent
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
                  >
                    Suivant
                  </PaginationNext>
                </Button>
              </PaginationContent>
            </Pagination>
          </div>
        </div>
      }
      records={
        <SkeletonsWhenLoading
          loadedUI={data.records.map((record) => (
            <Card key={record.ark}>
              <CardHeader className="">
                <CardTitle className="text-sm font-medium">
                  {record.paper_title}
                </CardTitle>
                <CardDescription>{record.date}</CardDescription>
              </CardHeader>
              <CardContent>
                <Suspense fallback={<div>Chargement du contexte...</div>}>
                  <VolumeRecordOccurrences record={record} />
                </Suspense>
              </CardContent>
            </Card>
          ))}
        />
      }
    />
  );
}

async function VolumeRecordOccurrences({ record }: { record: VolumeRecord }) {
  const { data, error } = await client.GET("/api/context", {
    params: {
      query: { ark: record.ark, terms: record.terms, url: record.url },
    },
  });

  if (error) {
    return <div>Erreur : {error.detail?.[0]?.msg}</div>;
  }

  const contextByPageNumber = R.groupBy(data, (c) => c.page_num);

  return (
    <div className="flex flex-col gap-7 overflow-auto max-h-96">
      {Object.entries(contextByPageNumber).map(([pageNumber, context]) => (
        <PageContext
          key={pageNumber}
          context={context}
          pageNumber={parseInt(pageNumber)}
          imageFetcher={
            <PageImage
              ark={record.ark}
              term={record.terms.at(0) ?? ""}
              page={parseInt(pageNumber)}
            />
          }
        />
      ))}
    </div>
  );
}

function PageContext({
  context,
  pageNumber,
  imageFetcher,
}: {
  context: Context;
  pageNumber: number;
  imageFetcher: React.ReactNode;
}) {
  const firstContextSnippet = context?.at(0);
  if (!firstContextSnippet) {
    return <div>Aucune contexte trouvée</div>;
  }
  return (
    <PageContextClientStateProvider>
      <div className="flex gap-2 items-center">
        <h1 className="text-lg font-bold">p. {pageNumber}</h1>
        <ShowImageButton />

        <CopyButton text={firstContextSnippet.page_url ?? ""} />
        <GrapherTooltip
          trigger={
            <Link href={firstContextSnippet.page_url ?? ""} target="_blank">
              <Button variant="ghost" className="text-gray-500">
                <ExternalLink />
              </Button>
            </Link>
          }
          content={<div>Voir sur Gallica</div>}
        />
      </div>
      <div className="flex flex-col gap-4 text-sm">
        {context.map((c, index) => (
          <span
            key={`${c.left_context}${c.page_num}${c.right_context}${index}`}
          >
            {c.left_context}{" "}
            <span className={" font-bold px-8 bg-yellow-300"}>{c.pivot}</span>{" "}
            {c.right_context}
          </span>
        ))}
      </div>
      <PageImageGate>{imageFetcher}</PageImageGate>
      <div className="w-full border mt-10" />
    </PageContextClientStateProvider>
  );
}

export function Feedback() {
  return (
    <a
      href="https://github.com/gleasonw/gallica-grapher/issues"
      target="_blank"
      className="text-gray-500 underline text-xs"
    >
      Un problème ? Une suggestion ? <br />
    </a>
  );
}
