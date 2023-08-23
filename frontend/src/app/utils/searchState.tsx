import { z } from "zod";

export const searchState = z.object({
  terms: z.string().array().optional(),
  year: z.coerce.number().optional(),
  end_year: z.coerce.number().optional(),
  month: z.coerce.number().optional(),
  day: z.coerce.number().optional(),
  source: z
    .literal("book")
    .or(z.literal("periodical"))
    .or(z.literal("all"))
    .optional(),
  link_term: z.string().optional(),
  link_distance: z.coerce.number().optional(),
  codes: z.string().array().optional(),
  limit: z.coerce.number().optional(),
  sort: z.literal("date").or(z.literal("relevance")).optional(),
  cursor: z.coerce.number().optional(),
  selected_term: z.string().optional(),
  context_year: z.coerce.number().optional(),
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
    console.log(result.error);
    return {};
  }
  return result.data;
}
