"use client";

import { HighchartsReact } from "highcharts-react-official";
import Highcharts from "highcharts";
import { useSearchState } from "../composables/useSearchState";
import { useSelectedTerm } from "../composables/useSelectedTerm";

export type NearbyData = [string, number][];

export function NearbyTermsChart({ data }: { data?: NearbyData }) {
  const { context_year } = useSearchState();
  const selectedTerm = useSelectedTerm();
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
