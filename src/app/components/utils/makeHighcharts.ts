import { GraphData } from "../models/dbStructs";

export const seriesColors = [
  "#7cb5ec",
  "#434348",
  "#90ed7d",
  "#f7a35c",
  "#8085e9",
  "#f15c80",
  "#e4d354",
  "#2b908f",
  "#f45b5b",
  "#91e8e1",
];

export function makeOptions(
  onSetExtremes: (e: any) => void,
  onSeriesClick: (e: any) => void,
  ticketData: GraphData[]
): Highcharts.Options {
  return {
    chart: {
      type: "line",
      zooming: {
        type: "x",
      },
    },
    rangeSelector: {
      enabled: false,
    },
    title: {
      text: "",
    },
    xAxis: {
      type: "datetime",
      events: {
        setExtremes: (e: Highcharts.AxisSetExtremesEventObject) =>
          onSetExtremes(e),
      },
    },
    yAxis: {
      title: {
        text: "Frequency",
      },
    },
    tooltip: {
      shared: true,
    },
    plotOptions: {
      series: {
        cursor: "pointer",
        lineWidth: 2,
        marker: {
          enabled: false,
          states: {
            hover: {
              enabled: true,
            },
            select: {
              enabled: true,
              fillColor: "#FFFFFF",
              radius: 5,
            },
          },
        },
      },
    },
    // @ts-ignore
    series: ticketData?.map((ticket, i) => ({
      name: ticket?.name,
      data: ticket?.data ?? [],
      color: seriesColors[i],
      point: {
        events: {
          click: (e: any) => {
            onSeriesClick(e.point);
          },
        },
      },
    })),
  };
}
