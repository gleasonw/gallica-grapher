import { z } from "zod";


export const tableParamSchema = z.object({
  terms: z.string(),
  year: z.coerce.number().nullish(),
  month: z.coerce.number().nullish(),
  day: z.coerce.number().nullish(),
  source: z
    .literal("book")
    .or(z.literal("periodical"))
    .or(z.literal("all"))
    .nullish(),
  link_term: z.string().nullish(),
  link_distance: z.coerce.number().nullish(),
  codes: z.string().array().nullish(),
  limit: z.coerce.number().nullish(),
  sort: z.literal("date").or(z.literal("relevance")).nullish(),
  cursor: z.number().nullish(),
});
