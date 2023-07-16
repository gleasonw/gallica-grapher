import { addQueryParamsIfExist } from "../utils/addQueryParamsIfExist";
import { GallicaResponse } from "./models/dbStructs";

export type QueryParams = {
  terms: string[];
  year?: number;
  end_year?: number;
  month?: number;
  end_month?: number;
  codes?: string[] | null;
  cursor?: number | null;
  limit?: number | null;
  link_term?: string | null;
  link_distance?: number | null;
  source?: "book" | "periodical" | "all";
  sort?: "date" | "relevance";
  row_split?: boolean | null;
  include_page_text?: boolean | null;
  all_context?: boolean | null;
};

export async function fetchContext(args: QueryParams) {
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
