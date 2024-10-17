import { DynamicRoute } from "next-typesafe-url";
import { boolean, z } from "zod";

export const Route = {
  searchParams: z.object({
    terms: z
      .union([z.string().transform((val) => [val]), z.array(z.string())])
      .optional()
      .default(["brazza"]),
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
    ark_selected_page: z.record(z.string(), z.number()).optional(),
    ark_show_image: z.record(z.string(), boolean()).optional(),
  }),
} satisfies DynamicRoute;
export type RouteType = typeof Route;

export type SearchParams = z.infer<(typeof Route)["searchParams"]>;
