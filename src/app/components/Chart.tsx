"use client";

import { useQuery } from "react-query";
import { useGraphState } from "../composables/useGraphState";
import { useSearchState } from "../composables/useSearchState";
import { InteractiveChart } from "./InteractiveChart";
import { SeriesResponse, fetchSeries } from "./fetchContext";
import React from "react";

export default function Chart() {
  const { terms, year, end_year } = useSearchState();
  const { grouping } = useGraphState();
  const [errorTerms, setErrorTerms] = React.useState<string[]>([]);
  const {
    data: seriesData,
    isLoading: isLoadingSeries,
    isError,
  } = useQuery({
    queryFn: async () => {
      const termsWithAtLeastOneElement = terms?.length ? terms : ["brazza"];

      // Map over terms and handle fetch errors including 404s
      const response = await Promise.all(
        termsWithAtLeastOneElement.map(async (term) => {
          const res = await fetchSeries({
            term: term,
            start_date: year,
            end_date: end_year,
            grouping: grouping,
          });

          // Check if the response is a 404 and throw an error if so
          if (!res.ok && res.status === 404) {
            setErrorTerms((prev) => [...prev, term]);
          }

          return res;
        })
      );

      const seriesData: SeriesResponse[] = [];

      for (const res of response) {
        if (res.ok) {
          const json = await res.json();
          seriesData.push(json as SeriesResponse);
        }
      }
      return seriesData;
    },
    onError: (error) => {
      console.error("Error fetching series:", error);
    },
    queryKey: ["series", terms, grouping, year, end_year],
  });

  if (isError) {
    return <div>Aucune donnée trouvée en Gallicagram</div>;
  }

  if (isLoadingSeries) {
    return (
      <div className="w-full h-32 flex justify-center items-center">
        En train de communiquer avec Gallicagram...{" "}
      </div>
    );
  }

  const errorTermsToDisplay = new Set(
    errorTerms.filter((term) => terms?.includes(term))
  );

  return (
    <div>
      {errorTermsToDisplay.size > 0 && (
        <div>
          Aucune donnée trouvée en Gallicagram pour les termes{" "}
          <span className="font-bold">
            {Array.from(errorTermsToDisplay).join(", ")}
          </span>
        </div>
      )}
      <InteractiveChart series={seriesData} />
    </div>
  );
}
