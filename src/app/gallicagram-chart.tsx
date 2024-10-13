"use client";
import { Route } from "@/src/app/routeType";
import { Series } from "@/src/app/types";
import { useSearchParams } from "next-typesafe-url/app";
import React from "react";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import { useNavigateWithLoading } from "@/src/app/providers";
import { makeOptions } from "@/src/app/makeHighcharts";
import Link from "next/link";

export function GallicaGramChart({ series }: { series: Series }) {
  //@ts-ignore
  const chartComponentRef = React.useRef<HighchartsReact.RefObject>(null);
  const { data } = useSearchParams(Route.searchParams);

  const { navigate } = useNavigateWithLoading();

  function handleSeriesClick(point: Highcharts.Point) {
    const chart = chartComponentRef.current?.chart;
    // @ts-ignore
    if (chart && chart.xAxis[0].plotLinesAndBands.length > 0) {
      chart.xAxis[0]?.removePlotLine("selectedLine");
      chart.xAxis[0]?.addPlotLine({
        value: point.x,
        color: "red",
        width: 2,
        id: "selectedLine",
      });
    }
    const date = new Date(point.category);
    navigate({
      route: "/",
      searchParams: {
        ...(data ?? {}),
        year: date.getUTCFullYear(),
        end_year: date.getUTCFullYear() + 1,
        cursor: 0,
      },
    });
  }

  function handleSetExtremes(e: Highcharts.AxisSetExtremesEventObject) {
    if (e.trigger === "zoom") {
      const minDate = new Date(e.min);
      if (minDate.toString() === "Invalid Date") {
        return navigate({
          route: "/",
          searchParams: {
            year: undefined,
            end_year: undefined,
            month: undefined,
            cursor: 0,
          },
        });
      }
      navigate({
        route: "/",
        searchParams: {
          year: minDate.getUTCFullYear(),
          end_year: minDate.getUTCFullYear() + 1,
          cursor: 0,
        },
      });
    }
  }

  const highchartsOpts = makeOptions(handleSetExtremes, handleSeriesClick, [
    series,
  ]);

  return (
    <div className={`transition-opacity w-full h-full flex w-full flex-col`}>
      <HighchartsReact
        highcharts={Highcharts}
        options={highchartsOpts}
        ref={chartComponentRef}
      />
      <span className="text-xs opacity-50 w-full flex">
        <Link
          href={"https://shiny.ens-paris-saclay.fr/app/gallicagram"}
          target="_blank"
          className="ml-auto underline"
        >
          Données n-gram de Gallicagram -- Benjamin Azoulay et Benoît de Courson
        </Link>
      </span>
    </div>
  );
}
