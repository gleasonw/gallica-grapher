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
import { ChevronLeft, ExternalLink, Image } from "lucide-react";
import {
  CopyButton,
  GrapherTooltip,
  PageImage,
} from "@/src/app/GrapherTooltip";
import { PageContextClientStateProvider } from "@/src/app/PageContextClientStateProvider";
import { client } from "@/src/app/utils";
import { PageContextScroller } from "@/src/app/PageContextScroller";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

type PageProps = InferPagePropsType<RouteType>;

// Site en français

async function GallicaGrapher({ searchParams }: PageProps) {
  return (
    <div className="flex flex-col h-screen overflow-hidden px-2 pb-2">
      <header className="py-4 flex flex-col gap-2">
        <div className="flex items-center space-x-2">
          <div className="relative flex-grow">
            <TermSearchInput />
          </div>
          <Filters />
        </div>
      </header>
      <div className="w-full h-52">
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
            records={Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="h-80 w-full animate-pulse bg-gray-200 rounded-md"
              />
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
      <div className="gap-14 grid grid-cols-1 max-h-full overflow-auto px-2 sm:px-20 ">
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
            <span className="text-nowrap font-medium">
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
                <CardTitle className="text-md font-medium">
                  {record.paper_title}
                </CardTitle>
                <CardDescription>{record.date}</CardDescription>
              </CardHeader>
              <CardContent>
                <Suspense
                  fallback={
                    <div className="h-80 flex items-center justify-center">
                      Chargement du contexte...
                    </div>
                  }
                >
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

function ensureMultiWordIsWrapped(terms: string[]) {
  return terms.map((t) =>
    t.trim().split(" ").length > 1 ? `"${t.trim()}"` : t.trim()
  );
}

async function VolumeRecordOccurrences({ record }: { record: VolumeRecord }) {
  const { data, error } = await client.GET("/api/context", {
    params: {
      query: {
        ark: record.ark,
        terms: ensureMultiWordIsWrapped(record.terms),
        url: record.url,
      },
    },
  });

  if (error) {
    return <div>Erreur : {error.detail?.[0]?.msg}</div>;
  }

  const firstPage = data.at(0)?.page_num;

  const contextByPageNumber = R.groupBy(data, (c) => c.page_num);
  const firstPageIndex = Object.keys(contextByPageNumber).findIndex(
    (k) => k === firstPage?.toString()
  );
  const sectionChunkSize = 3;
  const firstSectionToShow = Math.floor(firstPageIndex / sectionChunkSize);

  return (
    <div className="flex flex-col gap-7">
      <PageContextScroller
        sectionChunkSize={sectionChunkSize}
        startChunk={firstSectionToShow}
        pages={Object.entries(contextByPageNumber).map(
          ([pageNumber, context]) => (
            <PageContext
              key={pageNumber}
              context={context}
              pageNumber={parseInt(pageNumber)}
              paperData={{
                name: record.paper_title,
                date: record.date,
              }}
              imageFetcher={
                <PageImage
                  ark={record.ark}
                  term={record.terms.at(0) ?? ""}
                  page={parseInt(pageNumber)}
                />
              }
            />
          )
        )}
      />
    </div>
  );
}

function PageContext({
  context,
  pageNumber,
  imageFetcher,
  paperData,
}: {
  context: Context;
  pageNumber: number;
  imageFetcher: React.ReactNode;
  paperData: {
    name: string;
    date: string;
  };
}) {
  const firstContextSnippet = context?.at(0);
  if (!firstContextSnippet) {
    return <div>Aucune contexte trouvée</div>;
  }
  return (
    <PageContextClientStateProvider>
      <div className="flex items-center">
        <h1 className="font-medium">p. {pageNumber}</h1>
        <div className="mx-2" />
        <Dialog>
          <DialogTrigger asChild>
            <Button
              className=" text-gray-500"
              variant="ghost"
              aria-label="Voir l'image de la page"
            >
              <Image />
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogTitle>{paperData.name}</DialogTitle>
            <CardDescription>{paperData.date}</CardDescription>
            <DialogHeader>
              <Link
                href={firstContextSnippet.page_url ?? ""}
                className="underline text-blue-400"
                target="_blank"
              >
                p. {pageNumber}{" "}
              </Link>
            </DialogHeader>
            <DialogHeader>
              <DialogDescription>{imageFetcher}</DialogDescription>
            </DialogHeader>
          </DialogContent>
        </Dialog>
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
    </PageContextClientStateProvider>
  );
}
