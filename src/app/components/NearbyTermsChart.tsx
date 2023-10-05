"use client";

import { HighchartsReact } from "highcharts-react-official";
import Highcharts from "highcharts";
import { useSearchState } from "../composables/useSearchState";
import { useSelectedTerm } from "../composables/useSelectedTerm";
import { useQuery } from "react-query";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { apiURL } from "./apiURL";

export type NearbyData = [string, number][];

async function fetchNearby({
  term,
  year,
  month,
  max_n,
  sample_size,
}: {
  term: string;
  year: number;
  month?: number | null;
  max_n?: number | null;
  sample_size?: number | null;
}) {
  let baseUrl = `${apiURL}/api/mostTermsAtTime`;
  let url = addQueryParamsIfExist(baseUrl, {
    term,
    year,
    max_n,
    sample_size,
  });

  const response = await fetch(url);

  if (response.status !== 200) {
    return;
  }
  return (await response.json()) as [string, number][];
}

export function NearbyTermsChart() {
  const { context_year, month, max_n, sample_size } = useSearchState();
  const selectedTerm = useSelectedTerm();
  const { data, isLoading } = useQuery({
    queryKey: [context_year, month, max_n, sample_size, selectedTerm],
    queryFn: () =>
      fetchNearby({
        term: selectedTerm,
        year: context_year ?? 1882,
        month: month,
        max_n: max_n,
        sample_size: sample_size,
      }),
  });
  const highchartsOptions: Highcharts.Options = {
    chart: {
      type: "bar",
    },
    title: {
      text: "",
    },
    yAxis: {
      title: {
        text: "Count",
      },
    },
    xAxis: {
      categories: data?.map(([term, _]) => term),
      title: {
        text: null,
      },
      gridLineWidth: 1,
      lineWidth: 0,
    },
    series: [
      // @ts-ignore
      {
        name: "Count",
        data: data?.map(([_, count]) => count),
      },
    ],
  };

  return (
    <>
      {isLoading ? <BarSkeleton /> : null}
      {data && data.length > 0 && selectedTerm ? (
        <div className={"flex flex-col gap-5 m-2"}>
          <h1 className={"text-xl"}>
            Terms en proximité de {selectedTerm} en {context_year ?? 1882}
          </h1>
          <h2 className={"text-lg"}>
            {"Pris d'un échantillon de 50 occurrences"}
          </h2>
          <HighchartsReact
            highcharts={Highcharts}
            options={highchartsOptions}
          />
        </div>
      ) : (
        <div>
          {
            "Selectioner un point dans le graphe pour voir un échantillon de termes en proximité"
          }
        </div>
      )}
    </>
  );
}

function BarSkeleton() {
  return (
    <div className="p-6 space-y-4 flex flex-col">
      <div className="w-10/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-7/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-6/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-4/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-3/12 h-4 bg-gray-200 rounded animate-pulse" />
      <div className="w-2/12 h-4 bg-gray-200 rounded animate-pulse" />
    </div>
  );
}
