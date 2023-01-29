import { z } from "zod";
import { procedure, router } from "../trpc";

let apiURL: string;
if (process.env.NODE_ENV === "development") {
  apiURL = "http://0.0.0.0:8000";
} else {
  apiURL = "https://gallica-grapher-production.up.railway.app";
}

//snake case cuz that's what the API returns
export interface Paper {
  title: string;
  code: string;
  start_date: string;
  end_date: string;
}

export interface ProgressType {
  num_results_discovered: number;
  num_requests_to_send: number;
  num_requests_sent: number;
  estimate_seconds_to_completion: number;
  random_paper: string;
  random_text: string;
  state: "too_many_records" | "completed" | "error" | "no_records" | "running";
  backend_source: "gallica" | "pyllica";
}

export interface GraphData {
  request_id: number;
  data: {
    date: number; //year or unix seconds
    count: number;
  }[];
  name: string;
}

export interface GallicaResponse {
  records: GallicaRecord[];
  num_results: string;
}

export interface GallicaRecord {
  paper_title: string;
  paper_code: string;
  url: string;
  date: string;
  term: string;
  context: GallicaContext;
}

export interface GallicaContext {
  num_results: number;
  pages: GallicaPage[];
  ark: string;
}

export interface GallicaPage {
  page: string;
  context: string;
}

export const appRouter = router({
  hello: procedure
    .input(
      z.object({
        text: z.string(),
      })
    )
    .query(({ input }) => {
      return {
        greeting: `hello ${input.text}`,
      };
    }),
  papersSimilarTo: procedure
    .input(
      z.object({
        title: z.string(),
      })
    )
    .query(async ({ input }) => {
      if (!input.title) {
        return [];
      }
      const response = await fetch(`${apiURL}/api/papers/${input.title}`);
      const data = (await response.json()) as { papers: Paper[] };
      return data.papers;
    }),
  numPapers: procedure
    .input(
      z.object({
        from: z.number(),
        to: z.number(),
      })
    )
    .query(async ({ input }) => {
      const response = await fetch(
        `${apiURL}/api/numPapersOverRange/${input.from}/${input.to}`
      );
      const data = await response.json();
      return data;
    }),
  search: procedure
    .input(
      z.object({
        terms: z.array(z.string()),
        start_date: z.number().optional(),
        end_date: z.number().optional(),
        codes: z.array(z.string()).optional(),
        grouping: z
          .literal("year")
          .or(z.literal("month"))
          .or(z.literal("none")),
        num_results: z.number().optional(),
        start_index: z.number().optional(),
        num_workers: z.number().optional(),
        link_term: z.string().optional(),
        link_distance: z.number().optional(),
      })
    )
    .mutation(async ({ input }) => {
      const response = await fetch(`${apiURL}/api/init`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(input),
      });
      const data = (await response.json()) as { requestid: number };
      return data;
    }),
  progress: procedure
    .input(
      z.object({
        id: z.number(),
      })
    )
    .query(async ({ input }) => {
      const response = await fetch(`${apiURL}/poll/progress/${input.id}`);
      const data = (await response.json()) as ProgressType;
      return data;
    }),
  graphData: procedure
    .input(
      z.object({
        id: z.number(),
        backend_source: z.literal("gallica").or(z.literal("pyllica")),
        grouping: z.literal("year").or(z.literal("month")),
        smoothing: z.number(),
      })
    )
    .query(async ({ input }) => {
      const response = await fetch(
        `${apiURL}/api/graphData?request_id=${input.id}&backend_source=${input.backend_source}&grouping=${input.grouping}&average_window=${input.smoothing}`
      );
      const data = (await response.json()) as GraphData;
      return data;
    }),
  gallicaRecords: procedure
    .input(
      z.object({
        year: z.number().optional(),
        month: z.number().optional(),
        day: z.number().optional(),
        terms: z.array(z.string()),
        codes: z.array(z.string()).optional(),
        limit: z.number().nullish(),
        cursor: z.number().nullish(),
        link_term: z.string().optional(),
        link_distance: z.number().optional(),
      })
    )
    .query(async ({ input }) => {
      console.log(input);
      const limit = input.limit ?? 30;
      const { cursor } = input;
      if (input.terms.length === 0) {
        return {
          data: {
            records: [],
            num_results: 0,
          },
          nextCursor: null,
          previousCursor: null,
        };
      }
      let baseUrl = `${apiURL}/api/gallicaRecords`;
      let url = addQueryParamsIfExist(baseUrl, input);
      const response = await fetch(url);
      const data = (await response.json()) as GallicaResponse;
      let nextCursor = null;
      let previousCursor = cursor ?? 0;
      if (data.records && data.records.length > 0) {
        if (cursor) {
          nextCursor = cursor + limit;
        } else {
          nextCursor = limit;
        }
      }
      return {
        data,
        nextCursor,
        previousCursor,
      };
    }),
});

function addQueryParamsIfExist(url: string, params: Record<string, any>) {
  const urlParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && !Array.isArray(value)) {
      urlParams.append(key, value);
    } else if (Array.isArray(value)) {
      value.forEach((v) => {
        urlParams.append(key, v);
      });
    }
  });
  return `${url}?${urlParams.toString()}`;
}

// export type definition of API
export type AppRouter = typeof appRouter;
