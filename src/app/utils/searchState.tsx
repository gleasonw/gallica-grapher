import { z } from "zod";

export const searchState = z.object({
  terms: z.string().array().nullish(),
  year: z.coerce.number().nullish(),
  end_year: z.coerce.number().nullish(),
  month: z.coerce.number().nullish(),
  day: z.coerce.number().nullish(),
  source: z
    .literal("book")
    .or(z.literal("periodical"))
    .or(z.literal("all"))
    .optional(),
  link_term: z.string().nullish(),
  link_distance: z.coerce.number().nullish(),
  codes: z.string().array().nullish(),
  limit: z.coerce.number().nullish(),
  sort: z.literal("date").or(z.literal("relevance")).optional(),
  cursor: z.coerce.number().nullish(),
  selected_term: z.string().nullish(),
  context_year: z.coerce.number().nullish(),
  max_n: z.coerce.number().nullish(),
  sample_size: z.coerce.number().nullish(),
});

export type SearchState = z.infer<typeof searchState>;

export function getSearchStateFromURL(
  params: Record<string, any>
): SearchState {
  Object.entries(params).forEach(([key, value]) => {
    if (key === "codes" || key === "terms") {
      if (!Array.isArray(value)) {
        params[key] = [value];
      }
    }
  });
  const result = searchState.safeParse(params);
  if (!result.success) {
    return {};
  }
  return result.data;
}
