import { getGraphStateFromURL } from "../utils/getGraphStateFromURL";
import { getSearchStateFromURL } from "../utils/searchState";
import { InteractiveChart } from "./InteractiveChart";
import { SeriesResponse, fetchSeries } from "./fetchContext";

export default async function Chart({
  searchParams,
}: {
  searchParams: Record<string, string>;
}) {
  const { terms, year, end_year } = getSearchStateFromURL(searchParams);
  const { grouping } = getGraphStateFromURL(searchParams);
  const response = await Promise.allSettled(
    terms?.map(
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

  return <InteractiveChart series={seriesData} />;
}
