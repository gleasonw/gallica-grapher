"use client";

import { useQuery } from "react-query";
import { fetchContext } from "../components/fetchContext";
import { SearchState } from "../utils/searchState";
import { ContextInputForm } from "../components/ContextInputForm";
import ContextViewer from "../components/ContextViewer";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../components/design_system/card";
import { LoadingProvider } from "../components/LoadingProvider";

export interface ClientContextFetchProps {
  fetchParams: SearchState;
}

export function ClientContextFetch(props: ClientContextFetchProps) {
  const { fetchParams } = props;
  const contextParams = {
    ...fetchParams,
    terms: fetchParams?.terms ?? [],
    all_context: true,
  };
  const { data, isLoading } = useQuery({
    queryFn: async () => await fetchContext(contextParams),
    queryKey: ["context", fetchParams],
    keepPreviousData: true,
  });

  const maybeNumberResults = data?.num_results;

  let numResults = 0;
  if (
    maybeNumberResults &&
    !isNaN(maybeNumberResults) &&
    maybeNumberResults > 0
  ) {
    numResults = maybeNumberResults;
  }
  console.log(isLoading);

  return (
    <LoadingProvider>
      <ContextInputForm params={contextParams} num_results={numResults}>
        <DataViewer data={data} isLoading={isLoading} />
      </ContextInputForm>
    </LoadingProvider>
  );
}

export interface DataViewerProps {
  data?: Awaited<ReturnType<typeof fetchContext>>;
  isLoading: boolean;
}

export function DataViewer({ data, isLoading }: DataViewerProps) {
  if (!isLoading && !data) {
    return (
      <div className="aspect-video h-full flex justify-center items-center">
        Aucune donnée trouvée...{" "}
      </div>
    );
  }

  console.log(isLoading);

  const originURL = data?.origin_urls?.at(0);

  return (
    <div className={"flex flex-col gap-20 md:m-5"}>
      <OriginURL originURL={originURL} />
      {data?.records?.map((record, index) => (
        <Card key={`${record.ark}-${record.terms}-${index}`}>
          <CardHeader>
            <CardTitle>{record.paper_title}</CardTitle>
            <CardDescription>{record.date}</CardDescription>
          </CardHeader>
          <ContextViewer record={record} isLoading={isLoading} />
        </Card>
      ))}
    </div>
  );
}

export function OriginURL({ originURL }: { originURL?: string }) {
  if (!originURL) {
    return null;
  }

  const humanReadableQueryString = new URL(originURL).searchParams.get("query");
  return (
    <a href={originURL} className="text-blue-500" target="_blank">
      {humanReadableQueryString}
    </a>
  );
}
