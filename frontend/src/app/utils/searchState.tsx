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
});

export type SearchState = z.infer<typeof searchState>;

export function getSearchStateFromURL(
  params: Record<string, any>
): SearchState {
  const result = searchState.safeParse({
    ...params,
    terms: Array.isArray(params.terms) ? params.terms : [params.terms],
  });
  if (!result.success) {
    return {};
  }
  return result.data;
}
