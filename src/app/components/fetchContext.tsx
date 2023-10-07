import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { apiURL } from "./apiURL";
import { VolumeRecord } from "./models/dbStructs";
import { components, paths } from "../types";

export type ContextQueryParams =
  paths["/api/gallicaRecords"]["get"]["parameters"]["query"];

export type SeriesParams = paths["/api/series"]["get"]["parameters"]["query"];
export type SeriesResponse = components["schemas"]["Series"];

export type RowRecordResponse = components["schemas"]["RowRecordResponse"];

export async function fetchContext(args: ContextQueryParams) {
  let baseUrl = `${apiURL}/api/gallicaRecords`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
    all_context: args.all_context ?? false,
    limit: args.limit ?? 10,
  });
  const response = await fetch(url);
  if (response.status !== 200) {
    throw new Error("Error fetching context");
  }
  return (await response.json()) as RowRecordResponse;
}

export async function fetchSeries(args: SeriesParams): Promise<SeriesResponse> {
  let baseUrl = `${apiURL}/api/series`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
  });
  const response = await fetch(url);
  const data = (await response.json()) as SeriesResponse;
  return data;
}
