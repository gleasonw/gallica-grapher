import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { GallicaResponse, VolumeRecord } from "./models/dbStructs";

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

export async function fetchContext(args: ContextQueryParams) {
  let baseUrl = `https://gallica-grapher-production.up.railway.app/api/gallicaRecords`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
    all_context: false,
    row_split: true,
    limit: 10,
  });
  const response = await fetch(url);
  return (await response.json()) as GallicaResponse;
}

export async function fetchSRU(args: ContextQueryParams) {
  let baseUrl = `https://gallica-grapher-production.up.railway.app/api/sru`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
  });
  console.log("fetching from sru");
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
  const response = await fetch(
    `https://gallica-grapher-production.up.railway.app/api/volume?term=${term}&ark=${ark}`
  );
  const data = (await response.json()) as {
    pivot: string;
    right_context: string;
    left_context: string;
    page_num: number;
  }[];
  return data;
}
