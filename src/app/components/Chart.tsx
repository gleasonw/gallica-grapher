"use client";

import { makeOptions } from "./utils/makeHighcharts";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React from "react";
import { GraphData } from "./models/dbStructs";
import { useSearchState } from "../composables/useSearchState";
import { useGraphState } from "../composables/useGraphState";
import { SelectInput } from "./SelectInput";
import { InputLabel } from "./InputLabel";
import { useSubmit } from "./LoadingProvider";

export function Chart({ series }: { series?: GraphData[] }) {
  //@ts-ignore
  const chartComponentRef = React.useRef<HighchartsReact.RefObject>(null);
  const searchState = useSearchState();
  const { grouping } = useGraphState();
  const { year, end_year, terms } = searchState;

  const { handleSubmit } = useSubmit();

  React.useEffect(() => {
    function updateExtremes(from: number, to: number) {
      const chart = chartComponentRef.current?.chart;
      chart?.xAxis[0].setExtremes(Date.UTC(from, 0, 1), Date.UTC(to, 11, 31));
    }
    if (chartComponentRef.current) {
      const chart = chartComponentRef.current.chart;
      if (chart) {
        if (year && end_year) {
          updateExtremes(year, end_year);
        } else if (year) {
          updateExtremes(year, 1950);
        } else if (end_year) {
          updateExtremes(1789, end_year);
        } else {
          chart.xAxis[0].setExtremes(undefined, undefined);
        }
      }
    }
  }, [year, end_year]);

  function handleSeriesClick(point: Highcharts.Point) {
    const chart = chartComponentRef.current?.chart;
    // @ts-ignore
    if (chart && chart.xAxis[0].plotLinesAndBands.length > 0) {
      chart.xAxis[0].removePlotLine("selectedLine");
      chart.xAxis[0].addPlotLine({
        value: point.x,
        color: "red",
        width: 2,
        id: "selectedLine",
      });
    }

    const correspondingTerm = terms?.find((t) => t === point.series.name);
    if (correspondingTerm) {
      handleSubmit({ selected_term: correspondingTerm });
    }
    const date = new Date(point.category);
    if (grouping === "year") {
      handleSubmit({
        month: undefined,
        context_year: date.getUTCFullYear(),
        cursor: 0,
      });
    } else {
      handleSubmit({
        month: date.getUTCMonth() + 1,
        context_year: date.getUTCFullYear(),
        cursor: 0,
      });
    }
  }

  function handleSetExtremes(e: Highcharts.AxisSetExtremesEventObject) {
    if (e.trigger === "zoom") {
      const minDate = new Date(e.min);
      if (minDate.toString() === "Invalid Date") {
        handleSubmit({
          year: undefined,
          end_year: undefined,
          month: undefined,
          cursor: 0,
        });

        return;
      }
      if (grouping === "month") {
        handleSubmit({ month: minDate.getUTCMonth() + 1, cursor: 0 });
      }
      handleSubmit({
        context_year: minDate.getUTCFullYear(),
        cursor: 0,
      });
    }
  }

  const highchartsOpts = makeOptions(
    handleSetExtremes,
    handleSeriesClick,
    series ?? []
  );

  return (
    <div className={"relative"}>
      <HighchartsReact
        highcharts={Highcharts}
        options={highchartsOpts}
        ref={chartComponentRef}
      />
      <div
        className={
          "ml-10 absolute -top-20 right-2 z-40 mb-5 flex flex-row gap-5"
        }
      >
        <InputLabel label={"Grouping"}>
          <SelectInput
            options={["year", "month"] as const}
            onChange={(value) => handleSubmit({ grouping: value })}
            value={grouping ?? "month"}
          />
        </InputLabel>
      </div>
    </div>
  );
}
