"use client";

import { makeOptions } from "./utils/makeHighcharts";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React from "react";
import { GraphData } from "./models/dbStructs";
import { useSearchState } from "../composables/useSearchState";
import { SearchState } from "../utils/searchState";
import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { useRouter } from "next/navigation";
import {
  GraphState,
  getGraphStateFromURL,
} from "../utils/getGraphStateFromURL";
import { useGraphState } from "../composables/useGraphState";
import { SelectInput } from "./SelectInput";
import { InputLabel } from "./InputLabel";

export function Chart({ series }: { series?: GraphData[] }) {
  const chartComponentRef = React.useRef<HighchartsReact.RefObject>(null);
  const [isPending, startTransition] = React.useTransition();

  const searchState = useSearchState();
  const { grouping, smoothing } = useGraphState();
  const router = useRouter();
  const { year, end_year, terms } = searchState;

  function handleSubmit(params: SearchState & GraphState) {
    const url = addQueryParamsIfExist("/", {
      ...searchState,
      ...params,
    });
    startTransition(() => router.push(url, { scroll: false }));
  }

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
    const correspondingTerm = terms?.find((t) => t === point.series.name);
    if (correspondingTerm) {
      handleSubmit({ selected_term: correspondingTerm });
    }
    const date = new Date(point.category);
    if (grouping === "year") {
      handleSubmit({ month: undefined });
    } else {
      handleSubmit({ month: date.getUTCMonth() + 1 });
    }
    handleSubmit({
      year: date.getUTCFullYear(),
      end_year: date.getUTCFullYear() + 1,
    });
  }

  function handleSetExtremes(e: Highcharts.AxisSetExtremesEventObject) {
    if (e.trigger === "zoom") {
      const minDate = new Date(e.min);
      const maxDate = new Date(e.max);
      if (minDate.toString() === "Invalid Date") {
        handleSubmit({
          year: undefined,
          end_year: undefined,
          month: undefined,
        });

        return;
      }
      if (grouping === "month") {
        handleSubmit({ month: minDate.getUTCMonth() + 1 });
      }
      handleSubmit({
        year: minDate.getUTCFullYear(),
        end_year: maxDate.getUTCFullYear(),
      });
    }
  }

  const highchartsOpts = makeOptions(
    handleSetExtremes,
    handleSeriesClick,
    series
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
            options={["year", "month"]}
            onChange={(value: string) =>
              handleSubmit({ grouping: value as "year" | "month" })
            }
            value={grouping}
          />
        </InputLabel>
        <InputLabel label={"Smoothing"}>
          <SelectInput
            options={["0", "1", "2", "3", "4", "5", "10", "20", "50"]}
            onChange={(value: string) =>
              handleSubmit({ smoothing: parseInt(value) })
            }
            value={smoothing?.toString()}
          />
        </InputLabel>
      </div>
    </div>
  );
}
