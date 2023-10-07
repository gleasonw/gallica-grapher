"use client";

import { useQuery } from "react-query";
import { useGraphState } from "../composables/useGraphState";
import { useSearchState } from "../composables/useSearchState";
import { InteractiveChart } from "./InteractiveChart";
import { SeriesResponse, fetchSeries } from "./fetchContext";

export default function Chart() {
  const { terms, year, end_year } = useSearchState();
  const { grouping } = useGraphState();

  const { data: seriesData, isLoading: isLoadingSeries } = useQuery({
    queryFn: async () => {
      const termsWithAtLeastOneElement = terms?.length ? terms : ["brazza"];
      const response = await Promise.allSettled(
        termsWithAtLeastOneElement?.map(
          async (term) =>
            await fetchSeries({
              term: term,
              start_date: year,
              end_date: end_year,
              grouping: grouping,
            })
        ) ?? []
      );
      const seriesData = response.reduce<SeriesResponse[]>((acc, r) => {
        if (r.status === "fulfilled") {
          acc.push(r.value);
        }
        return acc;
      }, []);
      return seriesData;
    },
    queryKey: ["series", terms, grouping, year, end_year],
  });

  return <InteractiveChart series={seriesData} />;
}
