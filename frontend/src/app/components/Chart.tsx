import { makeOptions } from "./utils/makeHighcharts";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import React from "react";
import { GraphData } from "./models/dbStructs";

export function Chart({ series }: { series?: GraphData }) {
  const chartComponentRef = React.useRef<HighchartsReact.RefObject>(null);

  React.useEffect(() => {
    if (graphState.tickets?.some((ticket) => ticket.example)) {
      return;
    }
    const params = new URLSearchParams();
    if (graphState.tickets) {
      for (const ticket of graphState.tickets) {
        params.append("ticket_id", ticket.id.toString());
      }
    }
    window.history.replaceState(
      {},
      "",
      `${window.location.pathname.split("/")[0]}?${params.toString()}`
    );
  }, [graphState]);

  React.useEffect(() => {
    function updateExtremes(from: number, to: number) {
      const chart = chartComponentRef.current?.chart;
      chart?.xAxis[0].setExtremes(Date.UTC(from, 0, 1), Date.UTC(to, 11, 31));
    }
    if (chartComponentRef.current) {
      const chart = chartComponentRef.current.chart;
      if (chart) {
        if (searchFrom && searchTo) {
          updateExtremes(searchFrom, searchTo);
        } else if (searchFrom) {
          updateExtremes(searchFrom, 1950);
        } else if (searchTo) {
          updateExtremes(1789, searchTo);
        } else {
          chart.xAxis[0].setExtremes(undefined, undefined);
        }
      }
    }
  }, [searchFrom, searchTo]);

  function handleSeriesClick(point: Highcharts.Point) {
    if (!graphStateDispatch) return;
    const correspondingTicket = tickets?.find(
      (t) => t.terms[0] === point.series.name
    );
    if (correspondingTicket) {
      setSelectedTicket(correspondingTicket.id);
    }
    const date = new Date(point.category);
    if (grouping === "year") {
      setMonth(undefined);
    } else {
      setMonth(date.getUTCMonth() + 1);
    }
    setSearchFrom(date.getUTCFullYear());
    setSearchTo(date.getUTCFullYear() + 1);
  }

  function handleSetExtremes(e: Highcharts.AxisSetExtremesEventObject) {
    if (!graphStateDispatch) return;
    if (e.trigger === "zoom") {
      const minDate = new Date(e.min);
      const maxDate = new Date(e.max);
      if (minDate.toString() === "Invalid Date") {
        setMonth(undefined);
        setSearchFrom(undefined);
        setSearchTo(undefined);
        return;
      }
      if (grouping === "month") {
        setMonth(minDate.getUTCMonth() + 1);
      }
      setSearchFrom(minDate.getUTCFullYear());
      setSearchTo(maxDate.getUTCFullYear());
    }
  }

  const highchartsOpts = makeOptions(
    handleSetExtremes,
    handleSeriesClick,
    ticketData
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
        <InputLabel label={translation.grouping}>
          <SelectInput
            options={["year", "month"]}
            onChange={(value: string) => setGrouping(value as "year" | "month")}
            value={grouping}
          />
        </InputLabel>
        <InputLabel label={translation.smoothing}>
          <SelectInput
            options={["0", "1", "2", "3", "4", "5", "10", "20", "50"]}
            onChange={(value: string) => setSmoothing(parseInt(value))}
            value={smoothing.toString()}
          />
        </InputLabel>
      </div>
    </div>
  );
}
