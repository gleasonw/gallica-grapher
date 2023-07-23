import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { GallicaResponse } from "./models/dbStructs";

export type ContextQueryParams = {
  terms: string;
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
  let baseUrl = `https://gallica-grapher.ew.r.appspot.com/api/gallicaRecords`;
  let url = addQueryParamsIfExist(baseUrl, {
    ...args,
    all_context: true,
    row_split: true,
    limit: 10,
  });
  const response = await fetch(url);
  return (await response.json()) as GallicaResponse;
}
