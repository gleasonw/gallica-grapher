import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { apiURL } from "./apiURL";
import { VolumeRecord } from "./models/dbStructs";
import { components } from "../types";

export type ContextQueryParams = {
  terms: string[];
  year?: number;
  end_year?: number;
  month?: number;
  end_month?: number;
  codes?: string[];
  cursor?: number;
  limit?: number;
  link_term?: string;
  link_distance?: number;
  source?: "book" | "periodical" | "all";
  sort?: "date" | "relevance";
  row_split?: boolean;
  include_page_text?: boolean;
  all_context?: boolean;
};

export type RowRecordResponse = components["schemas"]["RowRecordResponse"];

export async function fetchContext(args: ContextQueryParams) {
  let baseUrl = `${apiURL}/api/gallicaRecords`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
    all_context: false,
    row_split: true,
    limit: 10,
  });
  const response = await fetch(url);
  if (response.status !== 200) {
    throw new Error("Error fetching context");
  }
  return (await response.json()) as RowRecordResponse;
}

export async function fetchSRU(args: ContextQueryParams) {
  let baseUrl = `${apiURL}/api/sru`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
  });
  console.log("fetching from sru", url);
  const response = await fetch(url);
  return (await response.json()) as {
    records: VolumeRecord[];
    total_records: number;
    origin_urls: string[];
  };
}

export async function fetchVolumeContext({
  ark,
  term,
}: {
  ark: string;
  term: string;
}) {
  const response = await fetch(`${apiURL}/api/volume?term=${term}&ark=${ark}`);
  const data = (await response.json()) as {
    pivot: string;
    right_context: string;
    left_context: string;
    page_num: number;
  }[];
  return data;
}
