import { z } from "zod";
import { procedure, router } from "../trpc";
import { addQueryParamsIfExist } from "../../utils/addQueryParamsIfExist";
import { GallicaResponse, GraphData, Paper, ProgressType } from "../../models/dbStructs";
import { tableParamSchema } from "../../models/tableParamSchema";

let apiURL: string;
if (process.env.NODE_ENV === "development") {
  apiURL = "http://0.0.0.0:8000";
} else {
  apiURL = "https://gallica-grapher-production.up.railway.app";
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
  gallicaRecords: procedure.input(tableParamSchema).query(async ({ input }) => {
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

// export type definition of API
export type AppRouter = typeof appRouter;
