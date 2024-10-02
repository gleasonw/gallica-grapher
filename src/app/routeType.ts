import { DynamicRoute } from "next-typesafe-url";
import { z } from "zod";

export const Route = {
  searchParams: z.object({
    terms: z.array(z.string()).optional(),
    codes: z.array(z.string()).optional(),
    cursor: z.number().optional(),
    limit: z.number().optional(),
    link_term: z.string().optional(),
    link_distance: z.number().optional(),
    year: z.coerce.number().optional(),
    month: z.coerce.number().optional(),
    end_year: z.coerce.number().optional(),
    end_month: z.coerce.number().optional(),
    source: z
      .literal("book")
      .or(z.literal("periodical"))
      .or(z.literal("all"))
      .optional(),
    sort: z.literal("date").or(z.literal("relevance")).optional(),
    ocrquality: z.number().optional(),
  }),
} satisfies DynamicRoute;
export type RouteType = typeof Route;
