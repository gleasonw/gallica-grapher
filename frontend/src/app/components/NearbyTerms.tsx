import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { NearbyTermsChart } from "./NearbyTermsChart";

export async function NearbyTerms({ params }: { params: Record<string, any> }) {
  let baseUrl = `https://gallica-grapher-production.up.railway.app/api/mostTermsAtTime`;
  let url = addQueryParamsIfExist(baseUrl, {
    term: params.selected_term ?? params.terms?.[0] ?? "brazza",
    year: params.context_year ?? 1882,
    month: params.month,
    max_n: params.max_n,
    sample_size: params.sample_size,
  });
  console.log(url);

  const response = await fetch(url);

  if (response.status !== 200) {
    return;
  }
  const parsedResponse = (await response.json()) as [string, number][];

  return <NearbyTermsChart data={parsedResponse} />;
}
