import { z } from "zod";

export const searchState = z.object({
  terms: z.string().optional(),
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
});

export type SearchState = z.infer<typeof searchState>;

export function getSearchStateFromURL(params: Record<string, any>): {
  searchState?: SearchState;
  error?: string;
} {
  const result = searchState.safeParse(params);
  if (!result.success) {
    return { error: result.error.message };
  }
  return { searchState: result.data };
}
